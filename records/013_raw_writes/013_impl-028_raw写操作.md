# impl-028：raw 写语法与脚本调用原文

仅记录语法命中和调用源码；脚本分支执行、历史文件版本、操作是否改变数据未由静态匹配证明。

## event 31

/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/.events/sessions/d3a309f4-d4c1-4b-dacf3c82bc8a080/events/31.json

```bash
cat > sql/marts/youtube__age_demographics_pivot.sql <<'SQL'
select
    age_pivot.date_day,
    age_pivot.video_id,
    age_pivot.country_code,
    age_pivot."13-17" as "13-17_view_percentage",
    age_pivot."18-24" as "18-24_view_percentage",
    age_pivot."25-34" as "25-34_view_percentage",
    age_pivot."35-44" as "35-44_view_percentage",
    age_pivot."45-54" as "45-54_view_percentage",
    age_pivot."55-64" as "55-64_view_percentage",
    age_pivot."65-" as "65-_view_percentage",
    video_lookup.video_title,
    video_lookup.published_at_date as video_published_date
from intermediate.int_youtube__age_pivot as age_pivot
left join intermediate.int_youtube__video as video_lookup
    on age_pivot.video_id = video_lookup.video_id
SQL
cat > sql/marts/youtube__gender_demographics_pivot.sql <<'SQL'
select
    gender_pivot.date_day,
    gender_pivot.video_id,
    gender_pivot.country_code,
    gender_pivot.female as female_view_percentage,
    gender_pivot.male as male_view_percentage,
    video_lookup.video_title,
    video_lookup.published_at_date as video_published_date
from intermediate.int_youtube__gender_pivot as gender_pivot
left join intermediate.int_youtube__video as video_lookup
    on gender_pivot.video_id = video_lookup.video_id
SQL
cat > sql/marts/youtube__demographics_report.sql <<'SQL'
with aggregated_demographics as (
    select
        date_day,
        video_id,
        country_code,
        case
            when sum(views_percentage) is null then null
            else greatest(0.0, least(1.0, sum(views_percentage)))
        end as total_views_percentage,
        count(distinct age_group) as age_groups_count,
        count(distinct gender) as genders_count,
        count(*) as records_count
    from intermediate.int_youtube__channel_demographics
    group by date_day, video_id, country_code
)
select
    aggregated_demographics.date_day,
    aggregated_demographics.video_id,
    aggregated_demographics.country_code,
    aggregated_demographics.total_views_percentage,
    aggregated_demographics.age_groups_count,
    aggregated_demographics.genders_count,
    aggregated_demographics.records_count,
    video_lookup.video_title,
    video_lookup.published_at_date as video_published_date
from aggregated_demographics
left join intermediate.int_youtube__video as video_lookup
    on aggregated_demographics.video_id = video_lookup.video_id
order by aggregated_demographics.date_day desc, aggregated_demographics.total_views_percentage desc
SQL
python run.py
```

脚本：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/run.py；final retained script; historical runtime version not established

CREATE TABLE/VIEW；源码行 119

```text

                    create_sql = f"CREATE OR REPLACE TABLE raw.{table_name} ({', '.join(column_defs)})"
                    self.conn.execute(create_sql)


```

INSERT/REPLACE INTO；源码行 125

```text
                        placeholders = ', '.join(['?' for _ in columns_info])
                        insert_sql = f"INSERT INTO raw.{table_name} VALUES ({placeholders})"
                        self.conn.executemany(insert_sql, data)

                    logger.info(f"  ✓ raw.{table_name}: {len(data)} rows")
```

## event 33

/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/.events/sessions/d3a309f4-d4c1-4b-dacf3c82bc8a080/events/33.json

```bash
python - <<'PY'
p='run.py'; s=open(p).read(); s=s.replace('tables_result = source_conn.execute("SHOW TABLES").fetchall()\n            source_tables = [table[0] for table in tables_result]', 'tables_result = source_conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = \'raw\' ORDER BY table_name").fetchall()\n            source_tables = [table[0] for table in tables_result]')
s=s.replace('source_conn.execute(f"SELECT * FROM {table_name}").fetchall()', 'source_conn.execute(f"SELECT * FROM raw.{table_name}").fetchall()')
s=s.replace('source_conn.execute(f"DESCRIBE {table_name}").fetchall()', 'source_conn.execute(f"DESCRIBE raw.{table_name}").fetchall()')
open(p,'w').write(s)
PY
rm -f youtube_analytics.duckdb && python run.py
```

脚本：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/run.py；final retained script; historical runtime version not established

CREATE TABLE/VIEW；源码行 119

```text

                    create_sql = f"CREATE OR REPLACE TABLE raw.{table_name} ({', '.join(column_defs)})"
                    self.conn.execute(create_sql)


```

INSERT/REPLACE INTO；源码行 125

```text
                        placeholders = ', '.join(['?' for _ in columns_info])
                        insert_sql = f"INSERT INTO raw.{table_name} VALUES ({placeholders})"
                        self.conn.executemany(insert_sql, data)

                    logger.info(f"  ✓ raw.{table_name}: {len(data)} rows")
```

## event 39

/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/.events/sessions/d3a309f4-d4c1-4b-dacf3c82bc8a080/events/39.json

```bash
python - <<'PY'
p='sql/marts/youtube__video_report.sql'
s=open(p).read().replace("""            else sum(average_view_duration_seconds * views) filter (where average_view_duration_seconds is not null)::double / sum(views)
""", """            else sum(average_view_duration_seconds * views) filter (where average_view_duration_seconds is not null)::double
                / sum(views) filter (where average_view_duration_seconds is not null)
""")
open(p,'w').write(s)
PY
python run.py > /tmp/pipeline_check.log 2>&1 && tail -28 /tmp/pipeline_check.log && python - <<'PY'
import duckdb
c=duckdb.connect('youtube_analytics.duckdb',read_only=True)
checks={
 'channel_basic row count preserved': "select (select count(*) from raw.youtube_channel_basic_data) >= (select count(*) from staging.stg_youtube__channel_basic)",
 'video IDs non-null': "select count(*) filter (where video_id is null)=0 from staging.stg_youtube__video",
 'age shares within bounds': "select count(*) filter (where \"13-17\" not between 0 and 1) = 0 from intermediate.int_youtube__age_pivot",
 'gender shares within bounds': "select count(*) filter (where female not between 0 and 1 or male not between 0 and 1) = 0 from intermediate.int_youtube__gender_pivot",
 'mart report keys unique': "select count(*)=count(distinct video_report_id) from marts.youtube__video_report",
 'positive records count': "select count(*) filter (where records_count < 1)=0 from marts.youtube__video_report",
}
for label,q in checks.items():
 try: print(label, c.execute(q).fetchone()[0])
 except Exception as e: print(label, 'ERROR',e)
PY
find sql -type f -name '*.sql' -print0 | xargs -0 grep -nE 'ref\(|;[[:space:]]*$' || true
```

脚本：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/run.py；final retained script; historical runtime version not established

CREATE TABLE/VIEW；源码行 119

```text

                    create_sql = f"CREATE OR REPLACE TABLE raw.{table_name} ({', '.join(column_defs)})"
                    self.conn.execute(create_sql)


```

INSERT/REPLACE INTO；源码行 125

```text
                        placeholders = ', '.join(['?' for _ in columns_info])
                        insert_sql = f"INSERT INTO raw.{table_name} VALUES ({placeholders})"
                        self.conn.executemany(insert_sql, data)

                    logger.info(f"  ✓ raw.{table_name}: {len(data)} rows")
```

## event 47

/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/.events/sessions/d3a309f4-d4c1-4b-dacf3c82bc8a080/events/47.json

```bash
cat > /workspace/result.md <<'MD'
【回复用户】

已按照 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 完成 YouTube Analytics 的 staging、intermediate 与 marts SQL。全部模型采用 DuckDB SQL、显式 `schema.table` 上游引用，没有 dbt `ref()`，SQL 文件末尾未添加分号。

## 交付文件

- **Staging:** `stg_youtube__channel_basic.sql`、`stg_youtube__channel_demographics.sql`、`stg_youtube__video.sql`
- **Intermediate:** `int_youtube__channel_basic.sql`、`int_youtube__channel_demographics.sql`、`int_youtube__age_pivot.sql`、`int_youtube__gender_pivot.sql`、`int_youtube__video.sql`
- **Marts:** `youtube__video_metadata.sql`、`youtube__video_report.sql`、`youtube__demographics_report.sql`、`youtube__age_demographics_pivot.sql`、`youtube__gender_demographics_pivot.sql`

## 实现和验证

- Staging 实现字段转换、验证、修正/置空和无效日期/视频记录的行级删除；Intermediate 实现逐行/窗口指标、人口统计透视与视频元数据解析；Marts 实现报表聚合、关联和指定输出字段。
- `python run.py` 成功完成所有模型：3 个 staging、5 个 intermediate、5 个 marts 均执行成功。输出行数依次为 **3,500 / 2,509 / 2,501**；intermediate 为 **3,500 / 2,509 / 2,504 / 1,671 / 2,501**；marts 为 **2,501 / 2,951 / 2,504 / 1,671 / 2,504**。
- 已检查 staging 行数及日期质量、透视占比上下界、非负报表总观看量、报表记录数等；所有执行检查均符合预期。非空 `video_report_id` 唯一。
- 运行时发现 `run.py` 从源数据库读取 `SHOW TABLES`、未限定 `raw` schema，因此对按 `raw` schema 存放的源表得到空表列表。已修正导入逻辑，从 `information_schema.tables` 读取 raw 表并通过 `raw.<table>` 读取，之后全流程通过。

## 合约数据不匹配及残余影响

1. 原始数据的 `channel_basic` 缺少 contract 字段 `channel_title`、`video_title`、`deleted`、`viewers`、`views_percentage`、部分 card/playlist 字段等；`video` 源缺少或类型与 contract 不同的缩略图、标签、语言、区域限制等字段。无法从源端恢复的 staging 字段填为类型正确的 NULL；这部分字段以及相应派生信息不可用，其余记录保留。
2. 数据中有 **2 条** channel_basic 记录的 `video_id` 为空。staging 契约允许该字段为空，且 intermediate 与报表业务逻辑要求保留源记录/分组，因此按要求保留；报表中对应 `video_report_id` 也为空（MD5 输入字符串因 `video_id` 为 NULL 而为空）。因此输入数据自身导致该报表键的 not-null/unique 契约测试无法对全部行成立，非空 ID 的键唯一性通过。未自行过滤这些行或伪造替代键，以免改变既定粒度和业务逻辑。
3. 视频表 `snippet_thumbnails`、`snippet_tags` 等原始字段类型为 DOUBLE 且样例中为空，不能提供 YAML 描述的 URL/标签字符串；视频 thumbnail URLs 因而为空，marts 按契约将 NULL 缩略图转换为空字符串。源字段的限制使 URL 解析无实际输入可验证。

上述边界按最小安全假设实施：源 schema 不存在的字段映射成类型化 NULL，不引入虚构信息；重复记录予以保留，未增加契约未要求的去重或排除规则。MD
cat /workspace/result.md
```

脚本：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/run.py；final retained script; historical runtime version not established

CREATE TABLE/VIEW；源码行 119

```text

                    create_sql = f"CREATE OR REPLACE TABLE raw.{table_name} ({', '.join(column_defs)})"
                    self.conn.execute(create_sql)


```

INSERT/REPLACE INTO；源码行 125

```text
                        placeholders = ', '.join(['?' for _ in columns_info])
                        insert_sql = f"INSERT INTO raw.{table_name} VALUES ({placeholders})"
                        self.conn.executemany(insert_sql, data)

                    logger.info(f"  ✓ raw.{table_name}: {len(data)} rows")
```

## event 51

/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/.events/sessions/d3a309f4-d4c1-4b-dacf3c82bc8a080/events/51.json

```bash
mkdir -p /workspace && cat > /workspace/result.md <<'MD'
【回复用户】

已按照 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 完成 YouTube Analytics 的 staging、intermediate 与 marts SQL。全部模型采用 DuckDB SQL、显式 `schema.table` 上游引用，没有 dbt `ref()`，SQL 文件末尾未添加分号。

## 交付文件

- **Staging:** `stg_youtube__channel_basic.sql`、`stg_youtube__channel_demographics.sql`、`stg_youtube__video.sql`
- **Intermediate:** `int_youtube__channel_basic.sql`、`int_youtube__channel_demographics.sql`、`int_youtube__age_pivot.sql`、`int_youtube__gender_pivot.sql`、`int_youtube__video.sql`
- **Marts:** `youtube__video_metadata.sql`、`youtube__video_report.sql`、`youtube__demographics_report.sql`、`youtube__age_demographics_pivot.sql`、`youtube__gender_demographics_pivot.sql`

## 实现和验证

- Staging 实现字段转换、验证、修正/置空和无效日期/视频记录的行级删除；Intermediate 实现逐行/窗口指标、人口统计透视与视频元数据解析；Marts 实现报表聚合、关联和指定输出字段。
- `python run.py` 成功完成所有模型：3 个 staging、5 个 intermediate、5 个 marts 均执行成功。输出行数依次为 **3,500 / 2,509 / 2,501**；intermediate 为 **3,500 / 2,509 / 2,504 / 1,671 / 2,501**；marts 为 **2,501 / 2,951 / 2,504 / 1,671 / 2,504**。
- 已检查 staging 行数及日期质量、透视占比上下界、非负报表总观看量、报表记录数等；所有执行检查均符合预期。非空 `video_report_id` 唯一。
- 运行时发现 `run.py` 从源数据库读取 `SHOW TABLES`、未限定 `raw` schema，因此对按 `raw` schema 存放的源表得到空表列表。已修正导入逻辑，从 `information_schema.tables` 读取 raw 表并通过 `raw.<table>` 读取，之后全流程通过。

## 合约数据不匹配及残余影响

1. 原始数据的 `channel_basic` 缺少 contract 字段 `channel_title`、`video_title`、`deleted`、`viewers`、`views_percentage`、部分 card/playlist 字段等；`video` 源缺少或类型与 contract 不同的缩略图、标签、语言、区域限制等字段。无法从源端恢复的 staging 字段填为类型正确的 NULL；这部分字段以及相应派生信息不可用，其余记录保留。
2. 数据中有 **2 条** channel_basic 记录的 `video_id` 为空。staging 契约允许该字段为空，且 intermediate 与报表业务逻辑要求保留源记录/分组，因此按要求保留；报表中对应 `video_report_id` 也为空（MD5 输入字符串因 `video_id` 为 NULL 而为空）。因此报表键的 not-null 契约测试对这两行不成立；非空 ID 的键唯一性通过。未自行过滤这些行或伪造替代键，以免改变既定粒度和业务逻辑。
3. 视频表 `snippet_thumbnails`、`snippet_tags` 等原始字段类型为 DOUBLE 且样例中为空，不能提供 YAML 描述的 URL/标签字符串；视频 thumbnail URLs 因而为空，marts 按契约将 NULL 缩略图转换为空字符串。源字段的限制使 URL 解析无实际输入可验证。

上述边界按最小安全假设实施：源 schema 不存在的字段映射成类型化 NULL，不引入虚构信息；重复记录予以保留，未增加契约未要求的去重或排除规则。
MD
cat /workspace/result.md
```

脚本：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/run.py；final retained script; historical runtime version not established

CREATE TABLE/VIEW；源码行 119

```text

                    create_sql = f"CREATE OR REPLACE TABLE raw.{table_name} ({', '.join(column_defs)})"
                    self.conn.execute(create_sql)


```

INSERT/REPLACE INTO；源码行 125

```text
                        placeholders = ', '.join(['?' for _ in columns_info])
                        insert_sql = f"INSERT INTO raw.{table_name} VALUES ({placeholders})"
                        self.conn.executemany(insert_sql, data)

                    logger.info(f"  ✓ raw.{table_name}: {len(data)} rows")
```

## event 55

/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/.events/sessions/d3a309f4-d4c1-4b-dacf3c82bc8a080/events/55.json

```bash
cat > result.md <<'MD'
【回复用户】

已按照 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 完成 YouTube Analytics 的 staging、intermediate 与 marts SQL。全部模型采用 DuckDB SQL、显式 `schema.table` 上游引用，没有 dbt `ref()`，SQL 文件末尾未添加分号。

## 交付文件

- **Staging:** `stg_youtube__channel_basic.sql`、`stg_youtube__channel_demographics.sql`、`stg_youtube__video.sql`
- **Intermediate:** `int_youtube__channel_basic.sql`、`int_youtube__channel_demographics.sql`、`int_youtube__age_pivot.sql`、`int_youtube__gender_pivot.sql`、`int_youtube__video.sql`
- **Marts:** `youtube__video_metadata.sql`、`youtube__video_report.sql`、`youtube__demographics_report.sql`、`youtube__age_demographics_pivot.sql`、`youtube__gender_demographics_pivot.sql`

## 实现和验证

- Staging 实现字段转换、验证、修正/置空和无效日期/视频记录的行级删除；Intermediate 实现逐行/窗口指标、人口统计透视与视频元数据解析；Marts 实现报表聚合、关联和指定输出字段。
- `python run.py` 成功完成所有模型：3 个 staging、5 个 intermediate、5 个 marts 均执行成功。输出行数依次为 **3,500 / 2,509 / 2,501**；intermediate 为 **3,500 / 2,509 / 2,504 / 1,671 / 2,501**；marts 为 **2,501 / 2,951 / 2,504 / 1,671 / 2,504**。
- 已检查 staging 行数及日期质量、透视占比上下界、非负报表总观看量、报表记录数等；所有执行检查均符合预期。非空 `video_report_id` 唯一。
- 运行时发现 `run.py` 从源数据库读取 `SHOW TABLES`、未限定 `raw` schema，因此对按 `raw` schema 存放的源表得到空表列表。已修正导入逻辑，从 `information_schema.tables` 读取 raw 表并通过 `raw.<table>` 读取，之后全流程通过。

## 合约数据不匹配及残余影响

1. 原始数据的 `channel_basic` 缺少 contract 字段 `channel_title`、`video_title`、`deleted`、`viewers`、`views_percentage`、部分 card/playlist 字段等；`video` 源缺少或类型与 contract 不同的缩略图、标签、语言、区域限制等字段。无法从源端恢复的 staging 字段填为类型正确的 NULL；这部分字段以及相应派生信息不可用，其余记录保留。
2. 数据中有 **2 条** channel_basic 记录的 `video_id` 为空。staging 契约允许该字段为空，且 intermediate 与报表业务逻辑要求保留源记录/分组，因此按要求保留；报表中对应 `video_report_id` 也为空（MD5 输入字符串因 `video_id` 为 NULL 而为空）。因此报表键的 not-null 契约测试对这两行不成立；非空 ID 的键唯一性通过。未自行过滤这些行或伪造替代键，以免改变既定粒度和业务逻辑。
3. 视频表 `snippet_thumbnails`、`snippet_tags` 等原始字段类型为 DOUBLE 且样例中为空，不能提供 YAML 描述的 URL/标签字符串；视频 thumbnail URLs 因而为空，marts 按契约将 NULL 缩略图转换为空字符串。源字段的限制使 URL 解析无实际输入可验证。

上述边界按最小安全假设实施：源 schema 不存在的字段映射成类型化 NULL，不引入虚构信息；重复记录予以保留，未增加契约未要求的去重或排除规则。
MD
cat result.md
```

脚本：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/run.py；final retained script; historical runtime version not established

CREATE TABLE/VIEW；源码行 119

```text

                    create_sql = f"CREATE OR REPLACE TABLE raw.{table_name} ({', '.join(column_defs)})"
                    self.conn.execute(create_sql)


```

INSERT/REPLACE INTO；源码行 125

```text
                        placeholders = ', '.join(['?' for _ in columns_info])
                        insert_sql = f"INSERT INTO raw.{table_name} VALUES ({placeholders})"
                        self.conn.executemany(insert_sql, data)

                    logger.info(f"  ✓ raw.{table_name}: {len(data)} rows")
```
