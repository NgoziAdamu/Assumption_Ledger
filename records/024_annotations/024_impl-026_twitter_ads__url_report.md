# impl-026 · twitter_ads__url_report

用途：**全量**；层：**marts**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**C**；把握：高。

campaign_id错取line_items外键而非匹配后的campaigns维度；8行单改L0全匹配。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-026_twitter_ads__url_report.md](../024_packages/024_impl-026_twitter_ads__url_report.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-026/docs/data_contract.yaml`。

```text
1777:     - name: twitter_ads__url_report
1778:       description: Daily placement-level metrics for promoted tweets that have a first expanded URL, enriched with URL components and campaign/account/tweet attributes; metrics are summed across the grouped dimensions.
1779:       grain: One row per unique combination of date_day, placement, account_id, account_name, campaign_id, campaign_name, line_item_id, line_item_name, promoted_tweet_id, tweet_id, tweet_name, tweet_full_text, base_url, url_host, url_path, utm_source, utm_medium, utm_campaign, utm_content, utm_term, expanded_url, display_url, currency
1780:       source_models:
1781:       - intermediate.int_twitter_ads__promoted_tweet_report_base
1782:       - intermediate.int_twitter_ads__promoted_tweets
1783:       - intermediate.int_twitter_ads__tweets
1784:       - intermediate.int_twitter_ads__tweet_url_first
1785:       - intermediate.int_twitter_ads__line_items
1786:       - intermediate.int_twitter_ads__campaigns
1787:       - intermediate.int_twitter_ads__accounts
1788:       business_logic: '- Start from intermediate.int_twitter_ads__promoted_tweet_report_base r (daily metrics by placement). - Join dimensions (LEFT JOINs in the query): • r.promoted_tweet_id → intermediate.int_twitter_ads__promoted_tweets pt • pt.tweet_id → intermediate.int_twitter_ads__tweets t • pt.tweet_id → intermediate.int_twitter_ads__tweet_url_first u (first URL per tweet) • pt.line_item_id → intermediate.int_twitter_ads__line_items li • li.campaign_id → intermediate.int_twitter_ads__campaigns c • r.account_id → intermediate.int_twitter_ads__accounts a - Apply filter: require u.expanded_url to be non-NULL, which effectively makes the join to u (and thus to pt) act as an inner join; other joins remain left and may yield NULL attributes. - Group by all selected dimensions exactly: date_day, placement, account_id, account_name, campaign_id, campaign_name, line_item_id, line_item_name, promoted_tweet_id, tweet_id, tweet_name, tweet_full_text, base_url, url_host, url_path, utm_source, utm_medium, utm_campaign, utm_content, utm_term, expanded_url, display_url, currency. - Aggregate using SUM over r.clicks, r.impressions, r.spend, r.spend_micro, r.url_clicks, r.total_conversions, r.total_conversions_sale_amount. • SUM ignores NULL inputs; if all values in a group are NULL, the result is NULL. • No rounding or unit conversion is applied; spend is in currency units and spend_micro in micro-units of the same currency. - No de-duplication is performed; multiple matches on joins replicate metric rows and are then aggregated within identical dimension sets.'
1789:       columns:
1790:       - name: date_day
1791:         data_type: DATE
1792:         description: Calendar day from r.date_day; defines the daily aggregation period.
1793:         tests:
1794:         - not_null
1795:       - name: placement
1796:         data_type: VARCHAR
1797:         description: Inventory placement from r.placement; used as a grouping dimension.
1798:       - name: account_id
1799:         data_type: VARCHAR
1800:         description: Twitter Ads account ID from r.account_id; used as a grouping dimension.
1801:         tests:
1802:         - not_null
1803:       - name: account_name
1804:         data_type: VARCHAR
1805:         description: Account display name from a.account_name; grouped and carried as-is; may be NULL.
1806:       - name: campaign_id
1807:         data_type: VARCHAR
1808:         description: Campaign ID from c.campaign_id via line_item → campaign; used as a grouping dimension; may be NULL.
1809:       - name: campaign_name
1810:         data_type: VARCHAR
1811:         description: Campaign name from c.campaign_name; grouped and carried as-is; may be NULL.
1812:       - name: line_item_id
1813:         data_type: VARCHAR
1814:         description: Line item ID from li.line_item_id via pt.line_item_id; used as a grouping dimension; may be NULL.
1815:       - name: line_item_name
1816:         data_type: VARCHAR
1817:         description: Line item name from li.line_item_name; grouped and carried as-is; may be NULL.
1818:       - name: promoted_tweet_id
1819:         data_type: VARCHAR
1820:         description: Promoted tweet ID from r.promoted_tweet_id; used as a grouping dimension.
1821:         tests:
1822:         - not_null
1823:       - name: tweet_id
1824:         data_type: BIGINT
1825:         description: Underlying tweet ID from pt.tweet_id; non-NULL due to URL filter; used as a grouping dimension.
1826:         tests:
1827:         - not_null
1828:       - name: tweet_name
1829:         data_type: VARCHAR
1830:         description: Tweet name label from t.tweet_name; grouped and carried as-is; may be NULL.
1831:       - name: tweet_full_text
1832:         data_type: VARCHAR
1833:         description: Full tweet text from t.tweet_full_text; grouped and carried as-is; may be NULL.
1834:       - name: base_url
1835:         data_type: VARCHAR
1836:         description: Expanded URL without query string from u.base_url; grouped and carried as-is; may be NULL.
1837:       - name: url_host
1838:         data_type: VARCHAR
1839:         description: Host component of the expanded URL from u.url_host; grouped and carried as-is; may be NULL.
1840:       - name: url_path
1841:         data_type: VARCHAR
1842:         description: Path component of the expanded URL from u.url_path; grouped and carried as-is; may be NULL or empty.
1843:       - name: utm_source
1844:         data_type: VARCHAR
1845:         description: UTM source from u.utm_source; grouped and carried as-is; NULL if not present.
1846:       - name: utm_medium
1847:         data_type: VARCHAR
1848:         description: UTM medium from u.utm_medium; grouped and carried as-is; NULL if not present.
1849:       - name: utm_campaign
1850:         data_type: VARCHAR
1851:         description: UTM campaign from u.utm_campaign; grouped and carried as-is; NULL if not present.
1852:       - name: utm_content
1853:         data_type: VARCHAR
1854:         description: UTM content from u.utm_content; grouped and carried as-is; NULL if not present.
1855:       - name: utm_term
1856:         data_type: VARCHAR
1857:         description: UTM term from u.utm_term; grouped and carried as-is; NULL if not present.
1858:       - name: expanded_url
1859:         data_type: VARCHAR
1860:         description: Full expanded URL from u.expanded_url; non-NULL due to filter; used as a grouping dimension.
1861:         tests:
1862:         - not_null
1863:       - name: display_url
1864:         data_type: VARCHAR
1865:         description: Display-friendly URL from u.display_url; grouped and carried as-is; may be NULL.
1866:       - name: currency
1867:         data_type: VARCHAR
1868:         description: Campaign currency code from c.currency; grouped and carried as-is; may be NULL.
1869:       - name: clicks
1870:         data_type: HUGEINT
1871:         description: Sum of r.clicks within each dimension group; NULLs ignored; NULL if all values are NULL.
1872:       - name: impressions
1873:         data_type: HUGEINT
1874:         description: Sum of r.impressions within each dimension group; NULLs ignored; NULL if all values are NULL.
1875:       - name: spend
1876:         data_type: DOUBLE
1877:         description: Sum of r.spend within each dimension group in currency units; NULLs ignored; NULL if all values are NULL.
1878:       - name: spend_micro
1879:         data_type: HUGEINT
1880:         description: Sum of r.spend_micro within each dimension group in micro-units; NULLs ignored; NULL if all values are NULL.
1881:       - name: url_clicks
1882:         data_type: HUGEINT
1883:         description: Sum of r.url_clicks within each dimension group; NULLs ignored; NULL if all values are NULL.
1884:       - name: total_conversions
1885:         data_type: HUGEINT
1886:         description: Sum of r.total_conversions within each dimension group; NULLs ignored; NULL if all values are NULL.
1887:       - name: total_conversions_sale_amount
1888:         data_type: DOUBLE
1889:         description: Sum of r.total_conversions_sale_amount within each dimension group in currency units; NULLs ignored; NULL if all values are NULL.
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/sql/marts/twitter_ads__url_report.sql`；SHA-256 `a3f856cb45726bf02f68982f327258c0817e08f1eb11ad699ac9420ff9f3d380`。

```text
1: select
2:     r.date_day, r.placement, r.account_id, a.account_name, li.campaign_id, c.campaign_name, pt.line_item_id, li.line_item_name, r.promoted_tweet_id, pt.tweet_id, t.tweet_name, t.tweet_full_text, u.base_url, u.url_host, u.url_path, u.utm_source, u.utm_medium, u.utm_campaign, u.utm_content, u.utm_term, u.expanded_url, u.display_url, c.currency,
3:     sum(r.clicks) as clicks, sum(r.impressions) as impressions, sum(r.spend) as spend,
4:     sum(r.spend_micro) as spend_micro, sum(r.url_clicks) as url_clicks,
5:     sum(r.total_conversions) as total_conversions,
6:     sum(r.total_conversions_sale_amount) as total_conversions_sale_amount
7: from intermediate.int_twitter_ads__promoted_tweet_report_base r
8: left join intermediate.int_twitter_ads__promoted_tweets pt on r.promoted_tweet_id = pt.promoted_tweet_id
9: left join intermediate.int_twitter_ads__tweets t on pt.tweet_id = t.tweet_id
10: left join intermediate.int_twitter_ads__tweet_url_first u on pt.tweet_id = u.tweet_id
11: left join intermediate.int_twitter_ads__line_items li on pt.line_item_id = li.line_item_id
12: left join intermediate.int_twitter_ads__campaigns c on li.campaign_id = c.campaign_id
13: left join intermediate.int_twitter_ads__accounts a on r.account_id = a.account_id
14: where u.expanded_url is not null
15: group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-026/sql/marts/twitter_ads__url_report.sql`；SHA-256 `e0229cb7b52b035af00ca8ffc6317e2d5a15cb7946b15aaf4a2a394ca2e80859`。

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
14:   u.base_url,
15:   u.url_host,
16:   u.url_path,
17:   u.utm_source,
18:   u.utm_medium,
19:   u.utm_campaign,
20:   u.utm_content,
21:   u.utm_term,
22:   u.expanded_url,
23:   u.display_url,
24:   c.currency,
25:   sum(r.clicks) as clicks,
26:   sum(r.impressions) as impressions,
27:   sum(r.spend) as spend,
28:   sum(r.spend_micro) as spend_micro,
29:   sum(r.url_clicks) as url_clicks,
30:   sum(r.total_conversions) as total_conversions,
31:   sum(r.total_conversions_sale_amount) as total_conversions_sale_amount
32: from intermediate.int_twitter_ads__promoted_tweet_report_base r
33: left join intermediate.int_twitter_ads__promoted_tweets pt on r.promoted_tweet_id = pt.promoted_tweet_id
34: left join intermediate.int_twitter_ads__tweets t on pt.tweet_id = t.tweet_id
35: left join intermediate.int_twitter_ads__tweet_url_first u on pt.tweet_id = u.tweet_id
36: left join intermediate.int_twitter_ads__line_items li on pt.line_item_id = li.line_item_id
37: left join intermediate.int_twitter_ads__campaigns c on li.campaign_id = c.campaign_id
38: left join intermediate.int_twitter_ads__accounts a on r.account_id = a.account_id
39: where u.expanded_url is not null
40: group by
41:   r.date_day, r.placement, r.account_id, a.account_name, c.campaign_id, c.campaign_name, li.line_item_id, li.line_item_name,
42:   r.promoted_tweet_id, pt.tweet_id, t.tweet_name, t.tweet_full_text, u.base_url, u.url_host, u.url_path, u.utm_source, u.utm_medium,
43:   u.utm_campaign, u.utm_content, u.utm_term, u.expanded_url, u.display_url, c.currency
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- campaign_projection（C）：**看到了但没提**；事件 9、10、19。
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

### 024_reruns_impl-026_twitter_ads__url_report.json
[024_reruns_impl-026_twitter_ads__url_report.json](../024_reruns_impl-026_twitter_ads__url_report.json)
上游：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-026/twitter.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1350|1350|8|8|否|
|L1|1350|1350|8|8|否|
|L2|1350|1350|8|8|否|
|L3|1350|1350|8|8|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"campaign_id":8}`
- L1：`{"campaign_id":8}`
- L2：`{"campaign_id":8}`
- L3：`{"campaign_id":8}`

#### baseline
私有SQL：`data/024_work/impl-026_twitter_ads__url_report/baseline.sql`；SHA-256 `a3f856cb45726bf02f68982f327258c0817e08f1eb11ad699ac9420ff9f3d380`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1350|1350|8|8|否|
|L1|1350|1350|8|8|否|
|L2|1350|1350|8|8|否|
|L3|1350|1350|8|8|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"campaign_id":8}`
- L1：`{"campaign_id":8}`
- L2：`{"campaign_id":8}`
- L3：`{"campaign_id":8}`

#### campaign_projection
主因；类别候选C。契约 campaign_id 明确来自匹配后的 campaigns。
相对本轮基线：行减少8，格减少8。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第2行、offset 50起替换；其他字节相同。
原表达式：
```sql
a.account_name, li.campaign_id
```

修改后：
```sql
a.account_name, c.campaign_id
```

私有SQL：`data/024_work/impl-026_twitter_ads__url_report/campaign_projection.sql`；SHA-256 `cd673301b3070068365ff206de3ad851d817b8545b95044c3bc273c85f4d9256`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1350|1350|0|0|是|
|L1|1350|1350|0|0|是|
|L2|1350|1350|0|0|是|
|L3|1350|1350|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`
## 规则问题

无。

