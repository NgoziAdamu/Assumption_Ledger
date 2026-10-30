# impl-026 · twitter_ads__promoted_tweet_report

用途：**全量**；层：**marts**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**C**；把握：高。

currency错取line_items而非契约campaigns；2012行改善为主因，另campaign_id错误保留未匹配外键影响20行。

参与因素：C：campaign_projection（行减10，格减510）。
标记：无。

## 材料与比较口径

[024_impl-026_twitter_ads__promoted_tweet_report.md](../024_packages/024_impl-026_twitter_ads__promoted_tweet_report.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-026/docs/data_contract.yaml`。

```text
1678:     - name: twitter_ads__promoted_tweet_report
1679:       description: Daily promoted tweet performance aggregated by placement and enriched with tweet, line item, campaign, and account attributes via left joins.
1680:       grain: One row per unique combination of date_day, placement, account_id, account_name, campaign_id, campaign_name, line_item_id, line_item_name, promoted_tweet_id, tweet_id, tweet_name, tweet_full_text, currency, is_deleted, promoted_tweet_status, campaign_status, line_item_status, approval_status, created_timestamp, updated_timestamp
1681:       source_models:
1682:       - intermediate.int_twitter_ads__promoted_tweet_report_base
1683:       - intermediate.int_twitter_ads__promoted_tweets
1684:       - intermediate.int_twitter_ads__tweets
1685:       - intermediate.int_twitter_ads__line_items
1686:       - intermediate.int_twitter_ads__campaigns
1687:       - intermediate.int_twitter_ads__accounts
1688:       business_logic: '- Start from the daily promoted tweet metrics base. - Left join promoted tweets by promoted_tweet_id. - Left join tweets by tweet_id from promoted tweets. - Left join line items by line_item_id from promoted tweets. - Left join campaigns by campaign_id from line items. - Left join accounts by account_id from the base. - Aggregate by these attributes: date_day, placement, account_id, account_name, campaign_id, campaign_name, line_item_id, line_item_name, promoted_tweet_id, tweet_id, tweet_name, tweet_full_text, currency, is_deleted, promoted_tweet_status, campaign_status, line_item_status, approval_status, created_timestamp, updated_timestamp. - For clicks, impressions, spend, spend_micro, url_clicks, total_conversions, and total_conversions_sale_amount: sum base values within each group; NULL inputs are ignored and a group of all NULLs yields NULL; numeric types are preserved with no rounding. - Left join behavior: if no match, the joined attributes are NULL; if multiple matches occur in a joined table, base rows are duplicated before aggregation, increasing summed metrics. - No explicit ordering is applied to the result.'
1689:       columns:
1690:       - name: date_day
1691:         data_type: DATE
1692:         description: Calendar date from the base metrics; grouping key.
1693:         tests:
1694:         - not_null
1695:       - name: placement
1696:         data_type: VARCHAR
1697:         description: Inventory placement from the base metrics; grouping key.
1698:       - name: account_id
1699:         data_type: VARCHAR
1700:         description: Ads account ID from the base metrics; grouping key.
1701:         tests:
1702:         - not_null
1703:       - name: account_name
1704:         data_type: VARCHAR
1705:         description: Account name from accounts; NULL if no match.
1706:       - name: campaign_id
1707:         data_type: VARCHAR
1708:         description: Campaign ID from campaigns; NULL if no match.
1709:       - name: campaign_name
1710:         data_type: VARCHAR
1711:         description: Campaign name from campaigns; NULL if no match.
1712:       - name: line_item_id
1713:         data_type: VARCHAR
1714:         description: Line item ID from line items; NULL if no match.
1715:       - name: line_item_name
1716:         data_type: VARCHAR
1717:         description: Line item name from line items; NULL if no match.
1718:       - name: promoted_tweet_id
1719:         data_type: VARCHAR
1720:         description: Promoted tweet ID from the base metrics; grouping key.
1721:         tests:
1722:         - not_null
1723:       - name: tweet_id
1724:         data_type: BIGINT
1725:         description: Tweet ID from promoted tweets; NULL if no match.
1726:       - name: tweet_name
1727:         data_type: VARCHAR
1728:         description: Tweet name from tweets; NULL if no match.
1729:       - name: tweet_full_text
1730:         data_type: VARCHAR
1731:         description: Tweet full text from tweets; NULL if no match.
1732:       - name: currency
1733:         data_type: VARCHAR
1734:         description: ISO currency from campaigns; NULL if no match; unit for spend.
1735:       - name: is_deleted
1736:         data_type: BOOLEAN
1737:         description: Soft-delete flag from promoted tweets; NULL if no match.
1738:       - name: promoted_tweet_status
1739:         data_type: VARCHAR
1740:         description: Lifecycle status from promoted tweets; NULL if no match.
1741:       - name: campaign_status
1742:         data_type: VARCHAR
1743:         description: Lifecycle status from campaigns; NULL if no match.
1744:       - name: line_item_status
1745:         data_type: VARCHAR
1746:         description: Lifecycle status from line items; NULL if no match.
1747:       - name: approval_status
1748:         data_type: VARCHAR
1749:         description: Approval status from promoted tweets; NULL if no match.
1750:       - name: created_timestamp
1751:         data_type: TIMESTAMP
1752:         description: Creation timestamp from promoted tweets; NULL if no match.
1753:       - name: updated_timestamp
1754:         data_type: TIMESTAMP
1755:         description: Last update timestamp from promoted tweets; NULL if no match.
1756:       - name: clicks
1757:         data_type: HUGEINT
1758:         description: Sum of clicks within each group; ignores NULLs; NULL if all inputs are NULL.
1759:       - name: impressions
1760:         data_type: HUGEINT
1761:         description: Sum of impressions within each group; ignores NULLs; NULL if all inputs are NULL.
1762:       - name: spend
1763:         data_type: DOUBLE
1764:         description: Sum of spend within each group in currency units; ignores NULLs; NULL if all inputs are NULL; no rounding.
1765:       - name: spend_micro
1766:         data_type: HUGEINT
1767:         description: Sum of spend_micro within each group; ignores NULLs; NULL if all inputs are NULL.
1768:       - name: url_clicks
1769:         data_type: HUGEINT
1770:         description: Sum of URL clicks within each group; ignores NULLs; NULL if all inputs are NULL.
1771:       - name: total_conversions
1772:         data_type: HUGEINT
1773:         description: Sum of total conversions within each group; ignores NULLs; NULL if all inputs are NULL.
1774:       - name: total_conversions_sale_amount
1775:         data_type: DOUBLE
1776:         description: Sum of conversion sale amount within each group; ignores NULLs; NULL if all inputs are NULL; no rounding.
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/sql/marts/twitter_ads__promoted_tweet_report.sql`；SHA-256 `1d05875d4d3003700049534a29b6e6f1b90b195794798853c8f5162d34aa2529`。

```text
1: select
2:     r.date_day, r.placement, r.account_id, a.account_name, li.campaign_id, c.campaign_name, pt.line_item_id, li.line_item_name, r.promoted_tweet_id, pt.tweet_id, t.tweet_name, t.tweet_full_text, li.currency, pt.is_deleted, pt.promoted_tweet_status, c.entity_status as campaign_status, li.entity_status as line_item_status, pt.approval_status, pt.created_timestamp, pt.updated_timestamp,
3:     sum(r.clicks) as clicks, sum(r.impressions) as impressions, sum(r.spend) as spend,
4:     sum(r.spend_micro) as spend_micro, sum(r.url_clicks) as url_clicks,
5:     sum(r.total_conversions) as total_conversions,
6:     sum(r.total_conversions_sale_amount) as total_conversions_sale_amount
7: from intermediate.int_twitter_ads__promoted_tweet_report_base r
8: left join intermediate.int_twitter_ads__promoted_tweets pt on r.promoted_tweet_id = pt.promoted_tweet_id
9: left join intermediate.int_twitter_ads__tweets t on pt.tweet_id = t.tweet_id
10: left join intermediate.int_twitter_ads__line_items li on pt.line_item_id = li.line_item_id
11: left join intermediate.int_twitter_ads__campaigns c on li.campaign_id = c.campaign_id
12: left join intermediate.int_twitter_ads__accounts a on r.account_id = a.account_id
13: group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-026/sql/marts/twitter_ads__promoted_tweet_report.sql`；SHA-256 `38e2af3e0eaa56927693056aad1d992e94b8a59b074736df8f1fd17ce9f8ee05`。

```text
1: select
2:   r.date_day,
3:   r.placement,
4:   r.account_id,
5:   a.account_name,
6:   c.campaign_id,
7:   c.campaign_name,
8:   li.line_item_id,
9:   li.line_item_name,
10:   r.promoted_tweet_id,
11:   pt.tweet_id,
12:   t.tweet_name,
13:   t.tweet_full_text,
14:   c.currency,
15:   pt.is_deleted,
16:   pt.promoted_tweet_status,
17:   c.entity_status as campaign_status,
18:   li.entity_status as line_item_status,
19:   pt.approval_status,
20:   pt.created_timestamp,
21:   pt.updated_timestamp,
22:   sum(r.clicks) as clicks,
23:   sum(r.impressions) as impressions,
24:   sum(r.spend) as spend,
25:   sum(r.spend_micro) as spend_micro,
26:   sum(r.url_clicks) as url_clicks,
27:   sum(r.total_conversions) as total_conversions,
28:   sum(r.total_conversions_sale_amount) as total_conversions_sale_amount
29: from intermediate.int_twitter_ads__promoted_tweet_report_base r
30: left join intermediate.int_twitter_ads__promoted_tweets pt on r.promoted_tweet_id = pt.promoted_tweet_id
31: left join intermediate.int_twitter_ads__tweets t on pt.tweet_id = t.tweet_id
32: left join intermediate.int_twitter_ads__line_items li on pt.line_item_id = li.line_item_id
33: left join intermediate.int_twitter_ads__campaigns c on li.campaign_id = c.campaign_id
34: left join intermediate.int_twitter_ads__accounts a on r.account_id = a.account_id
35: group by
36:   r.date_day, r.placement, r.account_id, a.account_name, c.campaign_id, c.campaign_name, li.line_item_id, li.line_item_name,
37:   r.promoted_tweet_id, pt.tweet_id, t.tweet_name, t.tweet_full_text, c.currency, pt.is_deleted, pt.promoted_tweet_status,
38:   c.entity_status, li.entity_status, pt.approval_status, pt.created_timestamp, pt.updated_timestamp
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- currency_source（C）：**看到了但没提**；事件 9、10、19。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。
event 9：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/.events/sessions/6ef6ea16-a56d-43-853379cddede9ee/events/9.json`；命令首行：`python - <<'PY'`。
event 10：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/.events/sessions/6ef6ea16-a56d-43-853379cddede9ee/events/10.json`；原始观察输出。
event 19：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/.events/sessions/6ef6ea16-a56d-43-853379cddede9ee/events/19.json`；命令首行：`cat >> /tmp/gen.py <<'PY'`。

最终报告原文（用于复核说明和工作清单边界）：

```
【回复用户】

Implemented the Twitter Ads SQL pipeline in `sql/staging/`, `sql/intermediate/`, and `sql/marts/` (12 staging, 12 intermediate, and 8 marts models). SQL uses DuckDB syntax, direct `schema.table` references, and no trailing semicolons.

**Verification:** Ran `python run.py` successfully. All configured models were created in their expected schemas, and the final run completed with `✅ Success` and no SQL errors.

**Implementation and data quality notes:**
- Staging applies field renames, timestamp/date parsing, status normalization and filtering, latest-version flags, spend conversions from micro-units, URL parsing, and tweet language validation.
- Intermediate models preserve configured source grains and derive conversion totals. Marts use left joins and aggregate metrics at configured dimensions, retaining unmatched dimension rows and SQL `SUM` NULL behavior.
- The raw Twitter report tables do not contain the contract’s conversion metric or conversion sale amount columns. Staging emits typed NULLs for these unavailable values; the intermediate logic treats them as zero per contract. The calculated totals consequently cannot represent actual conversions from this raw extract.
- The raw keyword report does not contain `keyword_id`; that field is derived from available `keyword` text, so uniqueness beyond keyword text is not guaranteed.
- The contract requests correction of unsupported timezones without specifying a fallback; invalid timezone values are set to `UTC`. UTC markers are removed before timestamp parsing. Tweet timestamps use a broad 2006–2100 bound because exact limits are unspecified.
- URL source `index` values are NULL in this extract. The first-URL model applies NULL-as-999999 ordering as specified; tied rows remain nondeterministic per the contract.

An initial test run exposed an unavailable source `keyword_id`, which caused the keyword intermediate and mart to fail. The staging projection was adjusted to derive it from `keyword`. The subsequent full run succeeded. The only unresolved contract/data limitation is the unavailable conversion fields in raw report sources.
```

## 查询

核实查询 **0** 条；代价档：**需要查业务说明**。含失败后重试的每条SQL；诊断查询不计入5条上限。
## 独立单点重跑

### 024_reruns_impl-026_twitter_ads__promoted_tweet_report.json
[024_reruns_impl-026_twitter_ads__promoted_tweet_report.json](../024_reruns_impl-026_twitter_ads__promoted_tweet_report.json)
上游：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-026/twitter.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2500|2500|2032|2532|否|
|L1|2500|2500|2032|2532|否|
|L2|2500|2500|2032|2532|否|
|L3|2500|2500|2032|2532|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":20,"promoted_tweet_id":20,"date_day":20,"placement":20,"campaign_id":20,"line_item_id":20,"tweet_id":20,"account_name":20,"approval_status":20,"campaign_name":20,"campaign_status":20,"clicks":20,"created_timestamp":20,"currency":2032,"impressions":20,"is_deleted":20,"line_item_name":20,"line_item_status":20,"promoted_tweet_status":20,"spend":20,"spend_micro":20,"total_conversions":20,"total_conversions_sale_amount":20,"tweet_name":20,"updated_timestamp":20,"url_clicks":20}`
- L1：`{"account_id":20,"promoted_tweet_id":20,"date_day":20,"placement":20,"campaign_id":20,"line_item_id":20,"tweet_id":20,"account_name":20,"approval_status":20,"campaign_name":20,"campaign_status":20,"clicks":20,"created_timestamp":20,"currency":2032,"impressions":20,"is_deleted":20,"line_item_name":20,"line_item_status":20,"promoted_tweet_status":20,"spend":20,"spend_micro":20,"total_conversions":20,"total_conversions_sale_amount":20,"tweet_name":20,"updated_timestamp":20,"url_clicks":20}`
- L2：`{"account_id":20,"promoted_tweet_id":20,"date_day":20,"placement":20,"campaign_id":20,"line_item_id":20,"tweet_id":20,"account_name":20,"approval_status":20,"campaign_name":20,"campaign_status":20,"clicks":20,"created_timestamp":20,"currency":2032,"impressions":20,"is_deleted":20,"line_item_name":20,"line_item_status":20,"promoted_tweet_status":20,"spend":20,"spend_micro":20,"total_conversions":20,"total_conversions_sale_amount":20,"tweet_name":20,"updated_timestamp":20,"url_clicks":20}`
- L3：`{"account_id":20,"promoted_tweet_id":20,"date_day":20,"placement":20,"campaign_id":20,"line_item_id":20,"tweet_id":20,"account_name":20,"approval_status":20,"campaign_name":20,"campaign_status":20,"clicks":20,"created_timestamp":20,"currency":2032,"impressions":20,"is_deleted":20,"line_item_name":20,"line_item_status":20,"promoted_tweet_status":20,"spend":20,"spend_micro":20,"total_conversions":20,"total_conversions_sale_amount":20,"tweet_name":20,"updated_timestamp":20,"url_clicks":20}`

#### baseline
私有SQL：`data/024_work/impl-026_twitter_ads__promoted_tweet_report/baseline.sql`；SHA-256 `1d05875d4d3003700049534a29b6e6f1b90b195794798853c8f5162d34aa2529`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2500|2500|2032|2532|否|
|L1|2500|2500|2032|2532|否|
|L2|2500|2500|2032|2532|否|
|L3|2500|2500|2032|2532|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":20,"promoted_tweet_id":20,"date_day":20,"placement":20,"campaign_id":20,"line_item_id":20,"tweet_id":20,"account_name":20,"approval_status":20,"campaign_name":20,"campaign_status":20,"clicks":20,"created_timestamp":20,"currency":2032,"impressions":20,"is_deleted":20,"line_item_name":20,"line_item_status":20,"promoted_tweet_status":20,"spend":20,"spend_micro":20,"total_conversions":20,"total_conversions_sale_amount":20,"tweet_name":20,"updated_timestamp":20,"url_clicks":20}`
- L1：`{"account_id":20,"promoted_tweet_id":20,"date_day":20,"placement":20,"campaign_id":20,"line_item_id":20,"tweet_id":20,"account_name":20,"approval_status":20,"campaign_name":20,"campaign_status":20,"clicks":20,"created_timestamp":20,"currency":2032,"impressions":20,"is_deleted":20,"line_item_name":20,"line_item_status":20,"promoted_tweet_status":20,"spend":20,"spend_micro":20,"total_conversions":20,"total_conversions_sale_amount":20,"tweet_name":20,"updated_timestamp":20,"url_clicks":20}`
- L2：`{"account_id":20,"promoted_tweet_id":20,"date_day":20,"placement":20,"campaign_id":20,"line_item_id":20,"tweet_id":20,"account_name":20,"approval_status":20,"campaign_name":20,"campaign_status":20,"clicks":20,"created_timestamp":20,"currency":2032,"impressions":20,"is_deleted":20,"line_item_name":20,"line_item_status":20,"promoted_tweet_status":20,"spend":20,"spend_micro":20,"total_conversions":20,"total_conversions_sale_amount":20,"tweet_name":20,"updated_timestamp":20,"url_clicks":20}`
- L3：`{"account_id":20,"promoted_tweet_id":20,"date_day":20,"placement":20,"campaign_id":20,"line_item_id":20,"tweet_id":20,"account_name":20,"approval_status":20,"campaign_name":20,"campaign_status":20,"clicks":20,"created_timestamp":20,"currency":2032,"impressions":20,"is_deleted":20,"line_item_name":20,"line_item_status":20,"promoted_tweet_status":20,"spend":20,"spend_micro":20,"total_conversions":20,"total_conversions_sale_amount":20,"tweet_name":20,"updated_timestamp":20,"url_clicks":20}`

#### currency_source
主因；类别候选C。契约 currency 明确来自 campaigns。
相对本轮基线：行减少2012，格减少2012。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第2行、offset 202起替换；其他字节相同。
原表达式：
```sql
li.currency
```

修改后：
```sql
c.currency
```

私有SQL：`data/024_work/impl-026_twitter_ads__promoted_tweet_report/currency_source.sql`；SHA-256 `4c77bef147d7e33d9028323619504562172b42d5d9854ee2c24df11becc62044`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2500|2500|20|520|否|
|L1|2500|2500|20|520|否|
|L2|2500|2500|20|520|否|
|L3|2500|2500|20|520|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":20,"promoted_tweet_id":20,"date_day":20,"placement":20,"campaign_id":20,"line_item_id":20,"tweet_id":20,"account_name":20,"approval_status":20,"campaign_name":20,"campaign_status":20,"clicks":20,"created_timestamp":20,"currency":20,"impressions":20,"is_deleted":20,"line_item_name":20,"line_item_status":20,"promoted_tweet_status":20,"spend":20,"spend_micro":20,"total_conversions":20,"total_conversions_sale_amount":20,"tweet_name":20,"updated_timestamp":20,"url_clicks":20}`
- L1：`{"account_id":20,"promoted_tweet_id":20,"date_day":20,"placement":20,"campaign_id":20,"line_item_id":20,"tweet_id":20,"account_name":20,"approval_status":20,"campaign_name":20,"campaign_status":20,"clicks":20,"created_timestamp":20,"currency":20,"impressions":20,"is_deleted":20,"line_item_name":20,"line_item_status":20,"promoted_tweet_status":20,"spend":20,"spend_micro":20,"total_conversions":20,"total_conversions_sale_amount":20,"tweet_name":20,"updated_timestamp":20,"url_clicks":20}`
- L2：`{"account_id":20,"promoted_tweet_id":20,"date_day":20,"placement":20,"campaign_id":20,"line_item_id":20,"tweet_id":20,"account_name":20,"approval_status":20,"campaign_name":20,"campaign_status":20,"clicks":20,"created_timestamp":20,"currency":20,"impressions":20,"is_deleted":20,"line_item_name":20,"line_item_status":20,"promoted_tweet_status":20,"spend":20,"spend_micro":20,"total_conversions":20,"total_conversions_sale_amount":20,"tweet_name":20,"updated_timestamp":20,"url_clicks":20}`
- L3：`{"account_id":20,"promoted_tweet_id":20,"date_day":20,"placement":20,"campaign_id":20,"line_item_id":20,"tweet_id":20,"account_name":20,"approval_status":20,"campaign_name":20,"campaign_status":20,"clicks":20,"created_timestamp":20,"currency":20,"impressions":20,"is_deleted":20,"line_item_name":20,"line_item_status":20,"promoted_tweet_status":20,"spend":20,"spend_micro":20,"total_conversions":20,"total_conversions_sale_amount":20,"tweet_name":20,"updated_timestamp":20,"url_clicks":20}`
### 024_supplement_reruns_impl-026_twitter_ads__promoted_tweet_report.json
[024_supplement_reruns_impl-026_twitter_ads__promoted_tweet_report.json](../024_supplement_reruns_impl-026_twitter_ads__promoted_tweet_report.json)
上游：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-026/twitter.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2500|2500|2032|2532|否|
|L1|2500|2500|2032|2532|否|
|L2|2500|2500|2032|2532|否|
|L3|2500|2500|2032|2532|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":20,"promoted_tweet_id":20,"date_day":20,"placement":20,"campaign_id":20,"line_item_id":20,"tweet_id":20,"account_name":20,"approval_status":20,"campaign_name":20,"campaign_status":20,"clicks":20,"created_timestamp":20,"currency":2032,"impressions":20,"is_deleted":20,"line_item_name":20,"line_item_status":20,"promoted_tweet_status":20,"spend":20,"spend_micro":20,"total_conversions":20,"total_conversions_sale_amount":20,"tweet_name":20,"updated_timestamp":20,"url_clicks":20}`
- L1：`{"account_id":20,"promoted_tweet_id":20,"date_day":20,"placement":20,"campaign_id":20,"line_item_id":20,"tweet_id":20,"account_name":20,"approval_status":20,"campaign_name":20,"campaign_status":20,"clicks":20,"created_timestamp":20,"currency":2032,"impressions":20,"is_deleted":20,"line_item_name":20,"line_item_status":20,"promoted_tweet_status":20,"spend":20,"spend_micro":20,"total_conversions":20,"total_conversions_sale_amount":20,"tweet_name":20,"updated_timestamp":20,"url_clicks":20}`
- L2：`{"account_id":20,"promoted_tweet_id":20,"date_day":20,"placement":20,"campaign_id":20,"line_item_id":20,"tweet_id":20,"account_name":20,"approval_status":20,"campaign_name":20,"campaign_status":20,"clicks":20,"created_timestamp":20,"currency":2032,"impressions":20,"is_deleted":20,"line_item_name":20,"line_item_status":20,"promoted_tweet_status":20,"spend":20,"spend_micro":20,"total_conversions":20,"total_conversions_sale_amount":20,"tweet_name":20,"updated_timestamp":20,"url_clicks":20}`
- L3：`{"account_id":20,"promoted_tweet_id":20,"date_day":20,"placement":20,"campaign_id":20,"line_item_id":20,"tweet_id":20,"account_name":20,"approval_status":20,"campaign_name":20,"campaign_status":20,"clicks":20,"created_timestamp":20,"currency":2032,"impressions":20,"is_deleted":20,"line_item_name":20,"line_item_status":20,"promoted_tweet_status":20,"spend":20,"spend_micro":20,"total_conversions":20,"total_conversions_sale_amount":20,"tweet_name":20,"updated_timestamp":20,"url_clicks":20}`

#### baseline
私有SQL：`data/024_supplement_work/impl-026_twitter_ads__promoted_tweet_report/baseline.sql`；SHA-256 `1d05875d4d3003700049534a29b6e6f1b90b195794798853c8f5162d34aa2529`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2500|2500|2032|2532|否|
|L1|2500|2500|2032|2532|否|
|L2|2500|2500|2032|2532|否|
|L3|2500|2500|2032|2532|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":20,"promoted_tweet_id":20,"date_day":20,"placement":20,"campaign_id":20,"line_item_id":20,"tweet_id":20,"account_name":20,"approval_status":20,"campaign_name":20,"campaign_status":20,"clicks":20,"created_timestamp":20,"currency":2032,"impressions":20,"is_deleted":20,"line_item_name":20,"line_item_status":20,"promoted_tweet_status":20,"spend":20,"spend_micro":20,"total_conversions":20,"total_conversions_sale_amount":20,"tweet_name":20,"updated_timestamp":20,"url_clicks":20}`
- L1：`{"account_id":20,"promoted_tweet_id":20,"date_day":20,"placement":20,"campaign_id":20,"line_item_id":20,"tweet_id":20,"account_name":20,"approval_status":20,"campaign_name":20,"campaign_status":20,"clicks":20,"created_timestamp":20,"currency":2032,"impressions":20,"is_deleted":20,"line_item_name":20,"line_item_status":20,"promoted_tweet_status":20,"spend":20,"spend_micro":20,"total_conversions":20,"total_conversions_sale_amount":20,"tweet_name":20,"updated_timestamp":20,"url_clicks":20}`
- L2：`{"account_id":20,"promoted_tweet_id":20,"date_day":20,"placement":20,"campaign_id":20,"line_item_id":20,"tweet_id":20,"account_name":20,"approval_status":20,"campaign_name":20,"campaign_status":20,"clicks":20,"created_timestamp":20,"currency":2032,"impressions":20,"is_deleted":20,"line_item_name":20,"line_item_status":20,"promoted_tweet_status":20,"spend":20,"spend_micro":20,"total_conversions":20,"total_conversions_sale_amount":20,"tweet_name":20,"updated_timestamp":20,"url_clicks":20}`
- L3：`{"account_id":20,"promoted_tweet_id":20,"date_day":20,"placement":20,"campaign_id":20,"line_item_id":20,"tweet_id":20,"account_name":20,"approval_status":20,"campaign_name":20,"campaign_status":20,"clicks":20,"created_timestamp":20,"currency":2032,"impressions":20,"is_deleted":20,"line_item_name":20,"line_item_status":20,"promoted_tweet_status":20,"spend":20,"spend_micro":20,"total_conversions":20,"total_conversions_sale_amount":20,"tweet_name":20,"updated_timestamp":20,"url_clicks":20}`

#### campaign_projection
参与因素；类别候选C。契约指定campaign id来自campaigns，20行缺匹配维度时原外键不等于NULL。
相对本轮基线：行减少10，格减少510。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第2行、offset 50起替换；其他字节相同。
原表达式：
```sql
a.account_name, li.campaign_id
```

修改后：
```sql
a.account_name, c.campaign_id
```

私有SQL：`data/024_supplement_work/impl-026_twitter_ads__promoted_tweet_report/campaign_projection.sql`；SHA-256 `4197eedf73c4dd5bbee36f09f33b726c441f283794a0d15770fc10b2331c69c8`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2500|2500|2022|2022|否|
|L1|2500|2500|2022|2022|否|
|L2|2500|2500|2022|2022|否|
|L3|2500|2500|2022|2022|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"currency":2022}`
- L1：`{"currency":2022}`
- L2：`{"currency":2022}`
- L3：`{"currency":2022}`

#### line_item_projection
不计参与因素；类别候选C。契约line item id来自匹配维度；独立检查。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第2行、offset 82起替换；其他字节相同。
原表达式：
```sql
c.campaign_name, pt.line_item_id
```

修改后：
```sql
c.campaign_name, li.line_item_id
```

私有SQL：`data/024_supplement_work/impl-026_twitter_ads__promoted_tweet_report/line_item_projection.sql`；SHA-256 `168770f08c7b46580d7ede8a1e70f551920aa4c40e5ddb2d1c9b442f58071385`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2500|2500|2032|2532|否|
|L1|2500|2500|2032|2532|否|
|L2|2500|2500|2032|2532|否|
|L3|2500|2500|2032|2532|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":20,"promoted_tweet_id":20,"date_day":20,"placement":20,"campaign_id":20,"line_item_id":20,"tweet_id":20,"account_name":20,"approval_status":20,"campaign_name":20,"campaign_status":20,"clicks":20,"created_timestamp":20,"currency":2032,"impressions":20,"is_deleted":20,"line_item_name":20,"line_item_status":20,"promoted_tweet_status":20,"spend":20,"spend_micro":20,"total_conversions":20,"total_conversions_sale_amount":20,"tweet_name":20,"updated_timestamp":20,"url_clicks":20}`
- L1：`{"account_id":20,"promoted_tweet_id":20,"date_day":20,"placement":20,"campaign_id":20,"line_item_id":20,"tweet_id":20,"account_name":20,"approval_status":20,"campaign_name":20,"campaign_status":20,"clicks":20,"created_timestamp":20,"currency":2032,"impressions":20,"is_deleted":20,"line_item_name":20,"line_item_status":20,"promoted_tweet_status":20,"spend":20,"spend_micro":20,"total_conversions":20,"total_conversions_sale_amount":20,"tweet_name":20,"updated_timestamp":20,"url_clicks":20}`
- L2：`{"account_id":20,"promoted_tweet_id":20,"date_day":20,"placement":20,"campaign_id":20,"line_item_id":20,"tweet_id":20,"account_name":20,"approval_status":20,"campaign_name":20,"campaign_status":20,"clicks":20,"created_timestamp":20,"currency":2032,"impressions":20,"is_deleted":20,"line_item_name":20,"line_item_status":20,"promoted_tweet_status":20,"spend":20,"spend_micro":20,"total_conversions":20,"total_conversions_sale_amount":20,"tweet_name":20,"updated_timestamp":20,"url_clicks":20}`
- L3：`{"account_id":20,"promoted_tweet_id":20,"date_day":20,"placement":20,"campaign_id":20,"line_item_id":20,"tweet_id":20,"account_name":20,"approval_status":20,"campaign_name":20,"campaign_status":20,"clicks":20,"created_timestamp":20,"currency":2032,"impressions":20,"is_deleted":20,"line_item_name":20,"line_item_status":20,"promoted_tweet_status":20,"spend":20,"spend_micro":20,"total_conversions":20,"total_conversions_sale_amount":20,"tweet_name":20,"updated_timestamp":20,"url_clicks":20}`
## 规则问题

无。

