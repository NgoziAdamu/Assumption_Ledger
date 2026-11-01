# impl-021_int_klaviyo__person_metrics（037 校准；解盲后工作结果）

主要原因：**Intent Misreading**；把握：中。本表不属于43张正式批次。

## 盲标与对比

盲标原件：`records/037_calibration_blind_sealed.json`，SHA-256 `b74b140d740d21b5aaab3febba23d1e6295bffce5b5759b906b15747ff97b6bf`。封存后不改。

盲标主因：Data Misconception；主点第 4 档。036：Intent Misreading，第 2 档。

盲标能构造连接不扩行的 P，但遗漏第5节“规格规定做法”边界的优先性：本契约直接定义 missing_day_count 为没有事件的 spine 日期数，并强调同日多事件不得改变计数。按定义实现即可改对，最终采用 Intent Misreading。报告“事件重复保留且照常计数”是泛指事件处理的策略，可记第2档；它没有点名 missing_day_count，不能升第1档。盲标把该句仅限于 attribution 的读法过窄。

019旧主要原因原样保留：`C`；不以旧类别推导新类别。

## 逐点依据

### 事件连接后仍把 count(*) 当作日期数

- 类别：Intent Misreading；角色：主要；把握：中。
- SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/sql/intermediate/int_klaviyo__person_metrics.sql`，第 7–10 行。
- 规模：017 两个替代单改各自均使 L0–L3 行 2→0、格 2→0；它们修复同一前提，不重复计点。
- 是否说出：第 2 档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

017 V3 在 agent 可见 staging 中查得 LRqEsZ、MCX88q 于同一天各两条事件；连接后行数膨胀，减去 distinct 事件天数会把重复事件当缺失天。无轨迹证据显示 agent 已正确理解连接后行数却仅手误；不能仅凭 distinct 关键字判代码写错。

解盲后分类说明：上述连接基数机制仍是事实，但主要分类按契约规定的 missing-day 计数定义归 Intent；原盲标 P 仅留在封存件，不作为最终 Data 条目。

证据文件：

- `records/017_queries_impl-021.json#V3`
- `records/017_reruns_impl-021.json#missing_count`
- `records/017_reruns_impl-021.json#spine_days_count`

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/41.json`，event 41 / `args.final_thought`：

> 事件 attribution 解析按契约优先级提取 JSON 子事件 ID，查找限定同一 `source_relation`；事件重复保留且照常计数。

证据在场：契约全文随初始 user message（event 1）直接送入，相关原句完整存在；不是被截断的读文件输出。没有另行读取契约的 run 事件。

event 1 / `message`：

> multiple events on a day do not change this count;

盲标能构造连接不扩行的 P，但遗漏第5节“规格规定做法”边界的优先性：本契约直接定义 missing_day_count 为没有事件的 spine 日期数，并强调同日多事件不得改变计数。按定义实现即可改对，最终采用 Intent Misreading。报告“事件重复保留且照常计数”是泛指事件处理的策略，可记第2档；它没有点名 missing_day_count，不能升第1档。盲标把该句仅限于 attribution 的读法过窄。

## 交付物核对

最终报告取 finish event 41 的 `args.final_thought`。本表最终 SQL 无注释，临时脚本不作交付物；扫描相关其他交付 SQL 注释未发现本处说明。

## 不确定与规则问题

Data/Intent 都可描述其机制；本次解盲后按规格规定指标的边界选 Intent。第2档通用说明覆盖范围也有宽窄读法；按共享事件重复处理的宽读记2，并明确非本指标具体披露。

两种单改修复同一个错误点，不重复计点。

Asana 的历史留存与单改重跑允许并列排序不同；不可把195行的留存基线与187行的重跑基线混算。校准表的最终类别与披露如经解盲修订，不能计入盲标一致率。
