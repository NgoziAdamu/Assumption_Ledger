"""Write the task 010 report with explicit candidate/verification distinctions."""

import json

from complete_dacomp_comparisons import ROOT,RECORDS


def main():
    total=json.loads((RECORDS/'010_summary.json').read_text())
    tasks=json.loads((RECORDS/'010_task_summary.json').read_text())
    validation=json.loads((RECORDS/'010_validation.json').read_text())
    rows=[json.loads(line) for line in (RECORDS/'010_table_verification.jsonl').read_text().splitlines()]
    table=['| 题目 | 内容支持的候选“今天” | L0 整表一致 | 仅日期一致 | 未能验证 | 已验证表的共同试验日 / 一致性限制 |',
           '|---|---|---:|---:|---:|---|']
    for task in tasks:
        dates=task['inferred_content_supported_candidates']
        label='、'.join(dates) if dates else '未能唯一确定'
        common=task['shared_successful_trial_dates']
        if not common:consistency='试验日集合没有共同日；逐表保留，未排除尚未共同测试的日期'
        elif len(common)>1:consistency='至少 '+ '、'.join(common)+' 均兼容，不能唯一定日'
        else:consistency='已验证表兼容 '+common[0]+('；另有未验证表' if task['unverified_tables'] else '')
        table.append(f"| {task['task']} | {label} | {task['l0_verified_tables']} | {task['date_only_verified_tables']} | {task['unverified_tables']} | {consistency} |")
    unknown=[task['task'] for task in tasks if not task['inferred_content_supported_candidates']]
    scopes=json.loads((RECORDS/'010_scope.json').read_text())
    starts=[a['execution_started']['Asia/Singapore'] for r in rows for a in r['attempts']]
    ends=[a['execution_finished']['Asia/Singapore'] for r in rows for a in r['attempts']]
    divergent=[t for t in tasks if not t['shared_successful_trial_dates']]
    divergent_text=[]
    for task in divergent:
        selected=[r for r in rows if r['task']==task['task'] and r['verification']!='未能验证']
        details='；'.join(r['table']+'：'+','.join(r['validated_dates']+r['date_only_validated_dates']) for r in selected if r['unique_day_not_claimed_for_weak_or_empty_output'])
        divergent_text.append(f"- {task['task']}：{details or '详见逐表结果'}。这些是已检验的兼容候选，不自动构成多个历史生成日期的证据。")
    date_only_no_timestamp=[r['task']+'/'+r['table'] for r in rows if r['verification']=='仅日期层面一致' and not r['has_timestamp_runtime_function']]
    text=f'''# DAComp DE-Impl：gold 日期推断与验证

## 任务

从 009 更正状态中“待标注 / 格式差异”且 gold SQL 命中 008 C9 时间写法的表出发，确定 **{len(tasks)} 题**；再扩展到这些题内全部含时间写法的 gold SQL。触发表 {scopes['trigger_count']} 张，最终核对 **{total['tables']} 个 gold SQL 目标**，其中 283 个有留存 gold 关系、20 个对应关系未找到。

全部重放只使用 gold SQL 和 gold 输入，未执行 agent SQL；004–009 的记录、报告和状态均保持原样。主要重放执行时间为 `{min(starts)}` 至 `{max(ends)}`（Asia/Singapore），跨 2026-10-28 / 29；文件名按用户指定保留 2026-10-28。

## 结论

**没有找到官方逐题 gold 生成日期记录。** 从当前留存 gold 内容得到 {total['tasks_with_content_supported_candidates']} 题的日期候选，并逐表重放验证；另外 {total['tasks_without_unique_day_inference']} 题（{', '.join(unknown)}）不能唯一确定“今天”。候选日、可复现的日期与官方生成日志是三种不同证据，本报告没有将它们混同。

全部 303 个目标的结果为：**L0 整表一致 {total['l0_verified']}、仅日期层面一致 {total['date_only_verified']}、未能验证 {total['unverified']}**。未能验证中包含 20 个缺 gold 关系目标和 1 个动态 gold view。表已复现不必然能唯一定日；例如同一节点在两个日期都能完整复现，就只能说明两日均兼容。

{chr(10).join(table)}

“仅日期一致”的 {total['date_only_verified']} 张中，{total['timestamp_only_date_verified']} 张 SQL 只含 CURRENT_TIMESTAMP 类函数；{total['date_only_with_DATE_and_TIMESTAMP']} 张混合日期和 timestamp 写法；另 {total['date_only_without_TIMESTAMP_function']} 张不含 timestamp 运行时函数，也只在去掉日期时间值的时刻后相同。均单列函数类型，未把“日期一致”解释为某种差异来源。

原始输入的大小、mtime、SHA-256 前后全部一致。009 中 12 张 impl-002 复比一致表已另加字段 **“官方评分为失败，复比一致”**，没有覆盖其旧状态。

## 详细发现

### 1. 查找直接记录

已亲自打开下列来源，未找到逐题 gold 执行日期表：

- DAComp 官方仓库根 README、dacomp-de/README.md、evaluation_suite/README.md。根 README 的 2025-12-08 是发布公告，下载说明只列出 gold 包位置和执行方式。[官方 README](https://github.com/ByteDance-Seed/DAComp)、[评测说明](https://github.com/ByteDance-Seed/DAComp/blob/main/dacomp-de/evaluation_suite/README.md)。
- arXiv **2512.04324v1 — DAComp: Benchmarking Data Agents across the Full Data Intelligence Lifecycle**，已核对编号和完整标题，读取正文构建说明与附录 10.1–10.2，检索 CURRENT_DATE、timestamp、生成 / bake date 等信息，未找到逐题日期。[arXiv 页面](https://arxiv.org/abs/2512.04324v1)、[全文及附录](https://arxiv.org/html/2512.04324v1)。
- Hugging Face gold 数据卡与上传 commit。2025-11-28 对应压缩包上传，不是数据库执行日期；本任务未下载该 2.99 GB 压缩包。[数据卡](https://huggingface.co/datasets/DAComp/dacomp-de-gold)、[上传记录](https://huggingface.co/datasets/DAComp/dacomp-de-gold/commit/2ec52c380c432d7223ca126bb304f5672e1a578a)。
- GitHub issue #5 / #6 中有第三方的时间相关观察；#5 提到 impl-002 日历末日 2025-10-18，与本次独立读取一致。没有把第三方推断当成维护者提供的生成日期。[issue #5](https://github.com/ByteDance-Seed/DAComp/issues/5)、[issue #6](https://github.com/ByteDance-Seed/DAComp/issues/6)。
- 逐题 gold 目录的文件清单；这些目录仅有 SQL / DuckDB 文件，未找到 README、JSON manifest 或生成日志。文件 mtime 只用于完整性检查，没有当成生成日期。

项目主页 `https://da-comp.github.io/` 返回 404；Hugging Face 文件树 API 通过 web 工具不可访问，但数据卡和上传 commit 可读。具体查询、原文行号、访问结果和目录清单在 [010_direct_sources.json](../records/010_direct_sources.json)。

### 2. 候选日期如何推出

每个内容候选都记录 gold 表、列、探测 SQL、观察值 / 行数、原 gold SQL 路径及时间写法的位置；[010_candidate_evidence.jsonl](../records/010_candidate_evidence.jsonl)和 [补充定向证据](../records/010_additional_candidate_evidence.json)可直接复核。主要方法包括直接输出的 CURRENT_DATE / CURRENT_TIMESTAMP 日期、日历端点、原始天数差的逆算。

代表性核查如下：

| 题目 | gold 内容与计算 | 候选 |
|---|---|---|
| impl-002 | intermediate.int_pendo__calendar_spine 的 MAX(date_day)=2025-10-18；原 SQL 的终点为 CURRENT_DATE + 1 week 且包含终点，减 7 天 | 2025-10-11 |
| impl-004 | 对未转换 lead，created_date + lead_age_days；2,407 行得到同一天，过滤 is_converted=false 以排除使用 converted_date 的分支 | 2025-10-24 |
| impl-011 | gold 日历表关联未解决 issue，3,233,030 行的 MAX(date_day)=2025-10-13；原 SQL 对这些 issue 使用 CURRENT_TIMESTAMP，并在末尾限制 date_day<=CURRENT_DATE | 2025-10-13 |
| impl-015 | int_quickbooks__customer_lifecycle 的 last_invoice_date + days_since_last_invoice，2,800 行均得到同一天 | 2025-10-13 |
| impl-017 | application_history 的 valid_until 中，107 个值不在上游 updated_at 值集中；原表达式为 COALESCE(LEAD(updated_at), CURRENT_TIMESTAMP)，日期均为 2025-10-24 | 候选 2025-10-24；该节点未能整表验证 |
| impl-019 | 日历最大日期为 2025-10-15，RANGE 的上界 CURRENT_DATE+1 day 不包含终点，因此“今天”就是最大日期。初次把端点当成包含而提出的 10-14 未通过，10-15 重放通过 | 2025-10-15 |
| impl-023 | Facebook staging 最早保留时间为 2023-10-17 11:36:36；结合两年筛选窗提出 2025-10-17。相邻日重放：10-16 为 140 行、10-17 完整匹配 138 行、10-18 为 135 行 | 2025-10-17 |

对 CASE 得分、比例、聚合或混合历史分支，不能把整个输出列直接当作 datediff 天数。早期探索中的此类逆算保留了 `raw_day_inverse_supported=false` 和限制说明，没有用于日期结论；需要分支条件的例子用上表的定向探测重新核实。

日期筛选只给约束时，最大业务日期也只是搜索候选。例如 impl-028 在 2024-01-30 与 01-31 都可完整重现全部 3 张表；不能因此认定生成日就是最大业务日期 01-30。impl-009、025 的全部相关表兼容 2025-10-12 和 10-13；impl-030 已通过表也兼容这两日。逐表尝试和仍未验证的节点分别保留。

### 3. 原样替换与 gold 输入重放

只按原文位置替换真正的运行时函数。每次替换记录文件、行 / 列、起止 offset、原文、替换文本、候选日期及替换前后 SHA-256。CURRENT_DATE 替换为 DATE 字面量；CURRENT_TIMESTAMP 等使用该日 **00:00:00 UTC 的 TIMESTAMPTZ 字面量**。历史时刻未恢复，午夜只是明确记录的占位；原会话时区也没有被反推。

注释、字符串、带引号的标识符，以及名叫 today 的列或 CTE 不作替换。SQL 本体其他字节不变：普通 SELECT 仅增加外层 CREATE OR REPLACE TABLE ... AS；原文件已有 DDL 的，执行其原语句。完整替换后 SQL 存在忽略的 data/ 下，git 内保留可无损重建的替换记录和 hash，不复制整份 gold SQL 仓库。

发现 3 份原 SQL 含 CRLF；其中一份早期加载把 CRLF 归一化为 LF，已按原始字节补跑。相应初步尝试明确标为不满足原字节保留条件，留在 `010_preliminary_*`，排除最终比较计数。最终全部 {total['final_attempts']} 次尝试通过原字节重建核对。

每题复制 gold 到 data/ 私有目录；每次目标执行前后恢复该目标为 gold，其他上游一直使用 gold 内容，只运行本节点 gold SQL。原库 READ_ONLY，执行 sandbox 中原项目 / 本仓库只读挂载、网络关闭，使用 scrubbed_env。没有执行 agent SQL、run.py 或模型调用。

**比较全部 gold 输出列**，包括可能不在官方 compare_cols 中的生成时间列；核对行数，并比较完整行元组的多重集合及重复次数。L0 值规范化沿用 LOWER / TRIM / CAST AS VARCHAR / NULL→'null'，不额外舍入。日期层面比较仅将明确的 ISO 日期时间取日期，数值和其他字符串保持 L0，未放宽数值精度。时间部分被舍弃，不只是在调整格式。

含 timestamp 函数且仅日期一致的表单列 `timestamp_only` / 函数列表。另有不含 timestamp 函数的日期层面匹配，不能以“时刻未知”解释其结果，亦未提升成 L0 通过。

### 4. 有限搜索及同题一致性

先尝试该表内容逆算、同题直接时钟 / 日历证据与其他已读到日期的候选。若未通过，再按主候选前后各 1 天逐日检查，明确记录三日邻域及理由（允许日期边界的一日不确定）；初始候选最多 8 个。未做无界日期搜索，未通过只表示已列出的候选和有限范围未能复现。

之后对缺少唯一日期证据的题增加了相邻日试验，并补查尚未测试该题主候选的节点。所有试验日、跳过原因、执行异常、行数和比较结果均记录在每表的 attempts；既有成功候选没有因补充试验而删除。

“共同试验日”是各已验证表成功候选集合的交集，未验证表不提供一致性证据。各表可兼容的其他试验日也逐表保留；这些差别不证明其真实历史生成日期不同。

{chr(10).join(divergent_text) if divergent_text else '本次所有已验证表均有共同兼容试验日；这仍不保证日期唯一，也不覆盖未验证节点。'}

动态例外：impl-022 的 marts.recharge__customer_details 在原 gold 中是含 CURRENT_TIMESTAMP 的 VIEW；当前查询值不是固定的历史物化输出。故该关系记“未能验证历史生成日期”，不把当前日期当成生成日期，也未修改原 view。

### 5. impl-002 的 12 张复比一致表

[010_impl002_replay_annotations.json](../records/010_impl002_replay_annotations.json)逐张新增 `official_scoring_match=false`、`replay_equal_gold=true`、`official_failed_replay_equal=true`、`display_label="官方评分为失败，复比一致"`。保留 `status_from_009` 与原评分 / 复比来源，`status_modified=false`；没有覆盖 009 的任何文件或状态。

## 证据来源

- [范围](../records/010_scope.json)、[逐题汇总](../records/010_task_summary.json)、[总汇总](../records/010_summary.json)。[逐表 CSV](../records/010_table_verification.csv) / [JSONL](../records/010_table_verification.jsonl)各 303 行；`010_verification_impl-NNN.json` 保存全部替换、候选与比较详情。
- [内容候选来源](../records/010_candidate_evidence.jsonl)、[补充原始探测](../records/010_additional_candidate_evidence.json)、[直接记录检索](../records/010_direct_sources.json)；逐题计划 `010_plan_impl-NNN.json` 含源 SQL 指纹、原文位置和 gold 列信息。
- [首批执行](../records/010_execution.json)、[补充执行](../records/010_additional_execution.json)、[相邻日执行](../records/010_boundary_execution.json)、[同题候选补查](../records/010_common_day_execution.json)。所有数据库 / 替换后的完整 SQL / 比较临时文件都在 data/010_*，不进 git。
- [完整性](../records/010_input_integrity.json)：{validation['original_input_files_unchanged']} 个输入文件前后大小、mtime、SHA-256 一致，其中 {validation['original_databases_unchanged']} 个原始 DuckDB；004–009 所有记录和报告保持原样，并交叉核对 009 的原库指纹。
- [验证](../records/010_validation.json)：{validation['replacement_attempts_audited']} 次尝试、{validation['replacement_spans_audited']} 处替换逐一核对；{len(validation['independent_gold_replays'])} 个代表节点另在私有副本重放，以独立 Counter / 日期解析实现复核；定向内容探测重现。[6 项规则测试](../records/010_tests.log)通过，覆盖 CRLF、注释 / 标识符、timestamp 占位、重复行、只舍时刻而不舍入数值及大表聚合。
- 实现：[准备 / 内容探测](../scripts/prepare_dacomp_gold_dates.py)、[替换 / 比较](../scripts/dacomp_gold_clock.py)、[gold 重放](../scripts/verify_dacomp_gold_dates.py)、[补充重放](../scripts/refine_dacomp_gold_dates.py)、[相邻日与共同日](../scripts/check_dacomp_gold_date_bounds.py)、[汇总](../scripts/finalize_dacomp_gold_dates.py)、[独立复核](../scripts/validate_dacomp_gold_dates.py)。Python 3.12.15、DuckDB 1.5.6、SQLGlot 30.25.0，未安装新依赖。

主要命令（相同前缀 `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`）：

```text
scripts/prepare_dacomp_gold_dates.py
scripts/verify_dacomp_gold_dates.py
scripts/refine_dacomp_gold_dates.py
scripts/refine_dacomp_gold_dates.py --merge
scripts/check_dacomp_gold_date_bounds.py
scripts/finalize_dacomp_gold_dates.py
scripts/check_dacomp_gold_date_bounds.py --complete-candidate-coverage
scripts/finalize_dacomp_gold_dates.py
scripts/validate_dacomp_gold_dates.py
-m unittest scripts/test_dacomp_gold_clock.py -v
scripts/write_dacomp_gold_date_report.py
```

定向逆算的探测 SQL、候选补充与 RANGE 端点修正均存于对应 evidence / plan，执行路径与参数在 execution 记录中。其他 gold SQL 内容未改动。

## 不确定或没查到的

没有官方逐题生成日志，也未恢复历史时刻或会话时区。{', '.join(unknown)} 没有唯一日期结论；多个日期可复现、动态 view 或条件不具备足够区分度时，保留未知，不以发布日期或文件 mtime 补全。

58 个目标未能按本次口径验证：20 个留存 gold 关系未找到、1 个为动态时钟 view，其余在已列候选 / 有限搜索下未达到全表 L0 或日期层面一致。缺表不作 0 行处理；执行异常和比较不一致分别原样记录，未判断其成因。即使某题有可信日期候选，也没有把未验证节点算作已验证。

## 建议的下一步

由用户和 Claude 决定后续如何使用日期候选和未验证清单。本任务不重跑 agent，不重算其得分，不改变 009 状态；需要唯一历史日期的题仍应寻找官方构建日志或可核实的固定时钟记录。
'''
    path=ROOT/'notes/010_2026-10-28_DAComp_gold日期推断与验证.md';path.write_text(text);print(path)


if __name__=='__main__':main()
