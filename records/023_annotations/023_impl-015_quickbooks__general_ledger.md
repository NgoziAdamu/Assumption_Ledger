# impl-015 · quickbooks__general_ledger

用途：**全量**；层：`marts`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**O**；把握：高；主要错误点：直接诊断（无正改善的单点排序）。

差异限于契约明确允许 engine-defined 的并列窗口累计顺序；排除两列累计后含键整表一致。

参与因素：无。

标记：无。

诊断见023_diagnostics：非累计列 L0 全匹配，存在窗口并列组。未通过追加排序键改变契约。

## 材料与比较口径

精简材料包：[023_impl-015_quickbooks__general_ledger.md](../023_packages/023_impl-015_quickbooks__general_ledger.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-015/docs/data_contract.yaml`；SHA-256 `c7c31842035fff7336164f7713a735dde48f8f77e19e992d2dae072b0144c51a`。
契约行 1901–2000：

```
1901:     - name: quickbooks__general_ledger
1902:       description: Unified general ledger combining bill, journal entry, and payment double-entry records enriched with account attributes, signed amounts, and running balances
1903:       grain: One row per unique_id (double-entry line item)
1904:       source_models:
1905:       - intermediate.int_quickbooks__bill_double_entry
1906:       - intermediate.int_quickbooks__journal_entry_double_entry
1907:       - intermediate.int_quickbooks__payment_double_entry
1908:       - intermediate.int_quickbooks__account_classifications
1909:       business_logic: '- Union all rows from intermediate.int_quickbooks__bill_double_entry, intermediate.int_quickbooks__journal_entry_double_entry, and intermediate.int_quickbooks__payment_double_entry; duplicates are preserved. - From the union, select: transaction_id, source_relation, index, transaction_date, customer_id, vendor_id, amount, converted_amount, account_id, class_id, department_id, transaction_type, transaction_source, created_at, updated_at. - Left join intermediate.int_quickbooks__account_classifications on (account_id, source_relation) to enrich account fields; if no match, account_* fields are NULL. - Compute unique_id by building a pipe-delimited string from transaction_id, source_relation, index, account_id, transaction_type, transaction_source in that exact order; treat NULL components as empty strings; hash this string with MD5 to produce a lowercase hex identifier. - Compute adjusted_amount: if account_transaction_type equals transaction_type, use amount; otherwise use amount multiplied by -1; if amount is NULL, adjusted_amount is NULL; when either type is NULL, treat as a mismatch and negate. - Compute adjusted_converted_amount the same way using converted_amount from the union (converted_amount itself is not included in the final output); NULLs propagate. - Compute running_balance as a cumulative sum of adjusted_amount within each (account_id, class_id, source_relation) partition, ordered by source_relation, transaction_date, account_id, class_id with rows unbounded preceding. - Compute running_converted_balance similarly using adjusted_converted_amount with the same partitioning and ordering. - Window ties on all ordering keys are engine-defined; cumulative sums skip NULL values and return NULL only when the entire frame is NULL. - Output one row per double-entry line enriched with account fields, signed amounts, and running balances.'
1910:       columns:
1911:       - name: unique_id
1912:         data_type: VARCHAR
1913:         description: Lowercase MD5 of the pipe-delimited string built from transaction_id, source_relation, index, account_id, transaction_type, transaction_source in that order; NULL inputs are treated as empty strings.
1914:       - name: transaction_id
1915:         data_type: VARCHAR
1916:         description: Source transaction identifier from the unioned double-entry models; preserved as-is.
1917:       - name: source_relation
1918:         data_type: VARCHAR
1919:         description: Originating model for the entry (bill, journal_entry, payment); used in the account join and in window partitioning and ordering.
1920:       - name: transaction_index
1921:         data_type: INTEGER
1922:         description: Line index within the source transaction (from 'index'); preserved as-is.
1923:       - name: transaction_date
1924:         data_type: DATE
1925:         description: Transaction posting date from source; used in window ordering.
1926:       - name: customer_id
1927:         data_type: VARCHAR
1928:         description: Customer identifier associated with the transaction when applicable; may be NULL.
1929:       - name: vendor_id
1930:         data_type: VARCHAR
1931:         description: Vendor identifier associated with the transaction when applicable; may be NULL.
1932:       - name: amount
1933:         data_type: DECIMAL(28,6)
1934:         description: Raw amount from source used to compute adjusted_amount; may be NULL.
1935:       - name: account_id
1936:         data_type: VARCHAR
1937:         description: Account identifier from source; used to join classifications and to partition running balances.
1938:       - name: class_id
1939:         data_type: VARCHAR
1940:         description: Class identifier from source; used to partition running balances; may be NULL.
1941:       - name: department_id
1942:         data_type: VARCHAR
1943:         description: Department identifier from source; preserved as-is; may be NULL.
1944:       - name: account_number
1945:         data_type: VARCHAR
1946:         description: Account number from classifications; NULL if no account match.
1947:       - name: account_name
1948:         data_type: VARCHAR
1949:         description: Account name from classifications; NULL if no account match.
1950:       - name: is_sub_account
1951:         data_type: BOOLEAN
1952:         description: TRUE if the account is a sub-account per classifications; NULL if no account match.
1953:       - name: parent_account_number
1954:         data_type: VARCHAR
1955:         description: Parent account number from classifications; NULL if none or no match.
1956:       - name: parent_account_name
1957:         data_type: VARCHAR
1958:         description: Parent account name from classifications; NULL if none or no match.
1959:       - name: account_type
1960:         data_type: VARCHAR
1961:         description: High-level account type from classifications (e.g., Asset, Liability); NULL if no match.
1962:       - name: account_sub_type
1963:         data_type: VARCHAR
1964:         description: Sub-type within the account_type from classifications; NULL if no match.
1965:       - name: financial_statement_helper
1966:         data_type: VARCHAR
1967:         description: Helper label from classifications indicating financial statement grouping; NULL if no match.
1968:       - name: account_current_balance
1969:         data_type: DECIMAL(28,6)
1970:         description: Current account balance from classifications; NULL if no match.
1971:       - name: account_class
1972:         data_type: VARCHAR
1973:         description: Classification label from classifications; NULL if no match.
1974:       - name: transaction_type
1975:         data_type: VARCHAR
1976:         description: Entry type from source (e.g., Debit/Credit or analogous); determines adjusted_amount sign.
1977:       - name: transaction_source
1978:         data_type: VARCHAR
1979:         description: Source subtype label from the unioned models; included in unique_id but not used in window partitioning.
1980:       - name: account_transaction_type
1981:         data_type: VARCHAR
1982:         description: Account-side transaction type from classifications; compared to transaction_type to set amount sign; may be NULL.
1983:       - name: created_at
1984:         data_type: TIMESTAMP WITH TIME ZONE
1985:         description: Row creation timestamp from source; preserved as-is.
1986:       - name: updated_at
1987:         data_type: TIMESTAMP WITH TIME ZONE
1988:         description: Row update timestamp from source; preserved as-is.
1989:       - name: adjusted_amount
1990:         data_type: DECIMAL(38,6)
1991:         description: 'Signed amount: equals amount when account_transaction_type equals transaction_type; otherwise amount multiplied by -1; NULL if amount is NULL.'
1992:       - name: adjusted_converted_amount
1993:         data_type: DECIMAL(38,12)
1994:         description: 'Signed converted amount derived from source converted_amount: equals converted_amount when types match, otherwise negated; NULL if converted_amount is NULL.'
1995:       - name: running_balance
1996:         data_type: DECIMAL(38,6)
1997:         description: Cumulative sum of adjusted_amount within each (account_id, class_id, source_relation) partition ordered by source_relation, transaction_date, account_id, class_id; NULLs are skipped.
1998:       - name: running_converted_balance
1999:         data_type: DECIMAL(38,12)
2000:         description: Cumulative sum of adjusted_converted_amount within each (account_id, class_id, source_relation) partition ordered by source_relation, transaction_date, account_id, class_id; NULLs are skipped.
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-015/agent/dacomp-de-impl-015/sql/marts/quickbooks__general_ledger.sql`，SHA-256 `4a55ee021407c2bd5381f6828e53d9caebd02189834feee6304b57765ba1b409`，行 1–15。

```
1: WITH entries AS (
2:  SELECT * FROM intermediate.int_quickbooks__bill_double_entry
3:  UNION ALL SELECT * FROM intermediate.int_quickbooks__journal_entry_double_entry
4:  UNION ALL SELECT * FROM intermediate.int_quickbooks__payment_double_entry
5: ), enriched AS (
6:  SELECT e.*,a.account_number,a.name account_name,a.is_sub_account,a.parent_account_number,a.parent_account_name,a.account_type account_type,a.account_sub_type,a.financial_statement_helper,a.balance account_current_balance,a.classification account_class,a.transaction_type account_transaction_type,
7:  md5(concat_ws('|',coalesce(e.transaction_id,''),coalesce(e.source_relation,''),coalesce(cast(e.index as varchar),''),coalesce(e.account_id,''),coalesce(e.transaction_type,''),coalesce(e.transaction_source,''))) unique_id,
8:  CASE WHEN a.transaction_type=e.transaction_type THEN e.amount ELSE e.amount*-1 END adjusted_amount,
9:  CASE WHEN a.transaction_type=e.transaction_type THEN e.converted_amount ELSE e.converted_amount*-1 END adjusted_converted_amount
10:  FROM entries e LEFT JOIN intermediate.int_quickbooks__account_classifications a ON e.account_id=a.account_id AND e.source_relation=a.source_relation
11: ), running AS (
12:  SELECT *,sum(adjusted_amount) OVER(PARTITION BY account_id,class_id,source_relation ORDER BY source_relation,transaction_date,account_id,class_id ROWS UNBOUNDED PRECEDING)::DECIMAL(38,6) running_balance,
13:  sum(adjusted_converted_amount) OVER(PARTITION BY account_id,class_id,source_relation ORDER BY source_relation,transaction_date,account_id,class_id ROWS UNBOUNDED PRECEDING)::DECIMAL(38,12) running_converted_balance FROM enriched
14: )
15: SELECT unique_id,transaction_id,source_relation,index transaction_index,transaction_date,customer_id,vendor_id,amount,account_id,class_id,department_id,account_number,account_name,is_sub_account,parent_account_number,parent_account_name,account_type,account_sub_type,financial_statement_helper,account_current_balance,account_class,transaction_type,transaction_source,account_transaction_type,created_at,updated_at,adjusted_amount,adjusted_converted_amount,running_balance,running_converted_balance FROM running
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-015/sql/marts/quickbooks__general_ledger.sql`，SHA-256 `12feebdffbd43dbc33f8d27009ac1cd38e8e419854b4ca4273faaa7e6922f6ef`，行 1–89。

```
1: with unioned_models as (
2:     select * from intermediate.int_quickbooks__bill_double_entry
3:     union all  
4:     select * from intermediate.int_quickbooks__journal_entry_double_entry
5:     union all
6:     select * from intermediate.int_quickbooks__payment_double_entry
7: ),
8: 
9: gl_union as (
10:     select transaction_id,
11:         source_relation,
12:         index,
13:         transaction_date,
14:         customer_id,
15:         vendor_id,
16:         amount,
17:         converted_amount,
18:         account_id,
19:         class_id,
20:         department_id,
21:         transaction_type,
22:         transaction_source,
23:         created_at,
24:         updated_at
25:     from unioned_models
26: ),
27: 
28: accounts as (
29:     select *
30:     from intermediate.int_quickbooks__account_classifications
31: ),
32: 
33: adjusted_gl as (
34:     select
35:         md5(concat(gl_union.transaction_id, '|', gl_union.source_relation, '|', gl_union.index, '|',
36:             gl_union.account_id, '|', gl_union.transaction_type, '|', gl_union.transaction_source)) 
37:             as unique_id,
38:         gl_union.transaction_id,
39:         gl_union.source_relation,
40:         gl_union.index as transaction_index,
41:         gl_union.transaction_date,
42:         gl_union.customer_id,
43:         gl_union.vendor_id,
44:         gl_union.amount,
45:         gl_union.account_id,
46:         gl_union.class_id,
47:         gl_union.department_id,
48:         accounts.account_number,
49:         accounts.name as account_name,
50:         accounts.is_sub_account,
51:         accounts.parent_account_number,
52:         accounts.parent_account_name,
53:         accounts.account_type,
54:         accounts.account_sub_type,
55:         accounts.financial_statement_helper,
56:         accounts.balance as account_current_balance,
57:         accounts.classification as account_class,
58:         gl_union.transaction_type,
59:         gl_union.transaction_source,
60:         accounts.transaction_type as account_transaction_type,
61:         gl_union.created_at,
62:         gl_union.updated_at,
63:         case when accounts.transaction_type = gl_union.transaction_type
64:             then gl_union.amount
65:             else gl_union.amount * -1
66:         end as adjusted_amount,
67:         case when accounts.transaction_type = gl_union.transaction_type
68:             then gl_union.converted_amount
69:             else gl_union.converted_amount * -1
70:         end as adjusted_converted_amount
71:     from gl_union
72: 
73:     left join accounts
74:         on gl_union.account_id = accounts.account_id
75:         and gl_union.source_relation = accounts.source_relation
76: ),
77: 
78: final as (
79:     select
80:         *,
81:         sum(adjusted_amount) over (partition by account_id, class_id, source_relation
82:             order by source_relation, transaction_date, account_id, class_id rows unbounded preceding) as running_balance,
83:         sum(adjusted_converted_amount) over (partition by account_id, class_id, source_relation
84:             order by source_relation, transaction_date, account_id, class_id rows unbounded preceding) as running_converted_balance
85:     from adjusted_gl
86: )
87: 
88: select *
89: from final
```

## 轨迹可见性与不确定性

**四档：看到了但没提**。

event 1 契约已说明 window ties；event 33 写出相同排序键的 ROWS 累计窗口；event 73 未说明本表并列顺序。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 1：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-015/agent/.events/sessions/b532323f-3e6c-45-9be5564f8a80cd2/events/1.json`。
- event 33：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-015/agent/.events/sessions/b532323f-3e6c-45-9be5564f8a80cd2/events/33.json`。
- event 73：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-015/agent/.events/sessions/b532323f-3e6c-45-9be5564f8a80cd2/events/73.json`。
## 查询

核实查询 **0** 条；核实代价档：**需要查业务说明**。诊断查询不计入 5 条上限。

未追加 agent 可见数据核实；判断依据为契约、SQL 和明确标为诊断的查询，不用 gold 结果证明 U。

### 诊断：排除两列窗口累计后整表含键比较

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|147000|147000|0|0|是|
|L1|147000|147000|0|0|是|
|L2|147000|147000|0|0|是|
|L3|147000|147000|0|0|是|

整表首次匹配档位：L0。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`

### 诊断：窗口排序键并列


```sql
SELECT count(*) tie_groups,sum(n) tied_rows FROM (SELECT count(*) n FROM g.marts.quickbooks__general_ledger GROUP BY account_id,class_id,source_relation,transaction_date HAVING count(*)>1)
```


```json
{"rows":[[5475,28106]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-015_quickbooks__general_ledger.json](../023_reruns_impl-015_quickbooks__general_ledger.json)

上游副本来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-015/quickbooks.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|147000|147000|22956|45912|否|
|L1|147000|147000|22956|45912|否|
|L2|147000|147000|22956|45912|否|
|L3|147000|147000|22956|45912|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"running_balance":22956,"running_converted_balance":22956}`
- L1：`{"running_balance":22956,"running_converted_balance":22956}`
- L2：`{"running_balance":22956,"running_converted_balance":22956}`
- L3：`{"running_balance":22956,"running_converted_balance":22956}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-015_quickbooks__general_ledger/baseline.sql`；SHA-256 `4a55ee021407c2bd5381f6828e53d9caebd02189834feee6304b57765ba1b409`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|147000|147000|23907|47814|否|
|L1|147000|147000|23907|47814|否|
|L2|147000|147000|23907|47814|否|
|L3|147000|147000|23907|47814|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"running_balance":23907,"running_converted_balance":23907}`
- L1：`{"running_balance":23907,"running_converted_balance":23907}`
- L2：`{"running_balance":23907,"running_converted_balance":23907}`
- L3：`{"running_balance":23907,"running_converted_balance":23907}`

## 原始表改动核对

event 39/40、43/44 报告 Unique file handle conflict；event45 改为 fetchdf/register/CREATE TABLE 导入，event46 成功。raw 类型改变但本次相关 invoice/vendor 表内容哈希相同。

初始/gold 一致而 agent 有变化，依第 3 节照常标注，不标不可评估。完整表清单见 [023_raw_trace_review.json](../023_raw_trace_review.json)；输入不变性另由前后指纹验证。

## 规则问题

无
