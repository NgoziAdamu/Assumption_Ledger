# impl-027 · xero__profit_and_loss_report

用途：**全量**；层：**marts**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**O**；把握：高。

契约允许并列项任意序的逐行累计，agent ROWS而gold默认RANGE使并列组累计相同；8个并列组，其他列L0全匹配。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-027_xero__profit_and_loss_report.md](../024_packages/024_impl-027_xero__profit_and_loss_report.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml`。

```text
1001:     - name: xero__profit_and_loss_report
1002:       description: Monthly profit and loss summary by account and tracking dimensions with revenue/expense split, net, and a month-level cumulative net
1003:       grain: One row per report_month per account_code per account_name per pl_category per pl_subcategory per region per department per project
1004:       source_models:
1005:       - intermediate.int_xero__general_ledger_fact
1006:       business_logic: '- Read journal lines from intermediate.int_xero__general_ledger_fact. - Derive calendar-based period fields from journal_date: fiscal_year (year), fiscal_month (month number 1–12), and fiscal_quarter (calendar quarter; used only in aggregation). - For each journal line: - revenue_amount = net_amount when account_class is REVENUE; otherwise 0. - expense_amount = absolute value of net_amount when account_class is EXPENSE; otherwise 0. - net_amount remains unchanged from source. - pl_category: - Revenue if account_class is REVENUE - Expenses if account_class is EXPENSE - Balance Sheet if account_class is ASSET, LIABILITY, or EQUITY - Other otherwise - pl_subcategory: - Operating Revenue if account_type is REVENUE - Operating Expenses if account_type is EXPENSE and account_code starts with "4" - Administrative Expenses if account_type is EXPENSE and account_code starts with "6" - Cost of Goods Sold if account_type is DIRECTCOSTS - Overhead if account_type is OVERHEADS - Depreciation if account_type is DEPRECIATN - Other otherwise - Aggregate monthly: - report_month = first day of the calendar month of journal_date. - Group by report_month, fiscal_year, fiscal_month, fiscal_quarter, account_code, account_name, pl_category, pl_subcategory, region, department, project. - Compute monthly_revenue = sum of revenue_amount, monthly_expenses = sum of expense_amount, monthly_net = sum of net_amount. - Produce final rows only where monthly_revenue is nonzero or monthly_expenses is nonzero; set period_type to "Monthly". - Output revenue = monthly_revenue, expenses = monthly_expenses, net_amount = monthly_net. - Compute cumulative_net within each report_month as a running total of monthly_net ordered alphabetically by pl_category, then by account_code ascending; when order keys tie, row order is nondeterministic. - Set report_generated_at to the execution timestamp (identical across rows within a run). - Order the final result by report_month descending, then by pl_category priority (Revenue first, Expenses second, then others), then by account_code ascending.'
1007:       columns:
1008:       - name: report_month
1009:         data_type: DATE
1010:         description: First calendar day of the month of journal_date
1011:         tests:
1012:         - not_null
1013:       - name: fiscal_year
1014:         data_type: INTEGER
1015:         description: Calendar year of journal_date
1016:       - name: fiscal_month
1017:         data_type: INTEGER
1018:         description: Calendar month number (1–12) of journal_date
1019:       - name: period_type
1020:         data_type: VARCHAR
1021:         description: Static period label; always 'Monthly'
1022:       - name: pl_category
1023:         data_type: VARCHAR
1024:         description: 'Category from account_class: Revenue, Expenses, Balance Sheet, or Other'
1025:       - name: pl_subcategory
1026:         data_type: VARCHAR
1027:         description: Detailed P&L subcategory from account_type and account_code prefix rules
1028:       - name: account_code
1029:         data_type: DOUBLE
1030:         description: Numeric ledger account code used for grouping and ordering; prefix checks treat it as a string; ordered ascending
1031:       - name: account_name
1032:         data_type: VARCHAR
1033:         description: Ledger account name from source; included in the monthly grouping
1034:       - name: revenue
1035:         data_type: DOUBLE
1036:         description: Monthly sum of revenue_amount (net_amount for REVENUE lines, else 0); may be negative; nulls ignored in sums; zero allowed
1037:       - name: expenses
1038:         data_type: DOUBLE
1039:         description: Monthly sum of expense_amount (absolute net_amount for EXPENSE lines, else 0); non-negative; nulls ignored in sums; zero allowed
1040:       - name: net_amount
1041:         data_type: DOUBLE
1042:         description: Monthly sum of raw net_amount across all journal lines in the grouping; sign preserved; nulls ignored in sums
1043:       - name: cumulative_net
1044:         data_type: DOUBLE
1045:         description: Within report_month, running total of net_amount ordered by pl_category (alphabetical) then account_code ascending; ties are nondeterministic; nulls ignored
1046:       - name: region
1047:         data_type: VARCHAR
1048:         description: Tracking dimension carried from source; part of the grouping; nulls preserved
1049:       - name: department
1050:         data_type: VARCHAR
1051:         description: Tracking dimension carried from source; part of the grouping; nulls preserved
1052:       - name: project
1053:         data_type: VARCHAR
1054:         description: Tracking dimension carried from source; part of the grouping; nulls preserved
1055:       - name: report_generated_at
1056:         data_type: TIMESTAMP WITH TIME ZONE
1057:         description: Execution timestamp for the run; identical across rows; time zone per engine configuration
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/marts/xero__profit_and_loss_report.sql`；SHA-256 `0fa815bac03d207a0f1034b0f97dc8de064353dff11924a9e9dcbd7f149c8fa8`。

```text
1: WITH journal_lines AS (
2:     SELECT
3:         TRY_CAST(journal_date AS DATE) AS journal_date,
4:         account_class,
5:         account_type,
6:         account_code,
7:         account_name,
8:         net_amount,
9:         region,
10:         department,
11:         project,
12:         CASE WHEN account_class = 'REVENUE' THEN net_amount ELSE 0 END AS revenue_amount,
13:         CASE WHEN account_class = 'EXPENSE' THEN abs(net_amount) ELSE 0 END AS expense_amount,
14:         CASE
15:             WHEN account_class = 'REVENUE' THEN 'Revenue'
16:             WHEN account_class = 'EXPENSE' THEN 'Expenses'
17:             WHEN account_class IN ('ASSET', 'LIABILITY', 'EQUITY') THEN 'Balance Sheet'
18:             ELSE 'Other'
19:         END AS pl_category,
20:         CASE
21:             WHEN account_type = 'REVENUE' THEN 'Operating Revenue'
22:             WHEN account_type = 'EXPENSE' AND starts_with(CAST(account_code AS VARCHAR), '4') THEN 'Operating Expenses'
23:             WHEN account_type = 'EXPENSE' AND starts_with(CAST(account_code AS VARCHAR), '6') THEN 'Administrative Expenses'
24:             WHEN account_type = 'DIRECTCOSTS' THEN 'Cost of Goods Sold'
25:             WHEN account_type = 'OVERHEADS' THEN 'Overhead'
26:             WHEN account_type = 'DEPRECIATN' THEN 'Depreciation'
27:             ELSE 'Other'
28:         END AS pl_subcategory
29:     FROM intermediate.int_xero__general_ledger_fact
30:     WHERE journal_date IS NOT NULL
31: ),
32: monthly AS (
33:     SELECT
34:         date_trunc('month', journal_date)::DATE AS report_month,
35:         year(journal_date)::INTEGER AS fiscal_year,
36:         month(journal_date)::INTEGER AS fiscal_month,
37:         quarter(journal_date)::INTEGER AS fiscal_quarter,
38:         account_code,
39:         account_name,
40:         pl_category,
41:         pl_subcategory,
42:         region,
43:         department,
44:         project,
45:         sum(revenue_amount)::DOUBLE AS revenue,
46:         sum(expense_amount)::DOUBLE AS expenses,
47:         sum(net_amount)::DOUBLE AS net_amount
48:     FROM journal_lines
49:     GROUP BY
50:         report_month, fiscal_year, fiscal_month, fiscal_quarter,
51:         account_code, account_name, pl_category, pl_subcategory,
52:         region, department, project
53: ),
54: filtered AS (
55:     SELECT *
56:     FROM monthly
57:     WHERE revenue <> 0 OR expenses <> 0
58: ),
59: with_cumulative AS (
60:     SELECT
61:         *,
62:         sum(net_amount) OVER (
63:             PARTITION BY report_month
64:             ORDER BY pl_category ASC, account_code ASC
65:             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
66:         ) AS cumulative_net
67:     FROM filtered
68: )
69: SELECT
70:     report_month,
71:     fiscal_year,
72:     fiscal_month,
73:     'Monthly' AS period_type,
74:     pl_category,
75:     pl_subcategory,
76:     account_code,
77:     account_name,
78:     revenue,
79:     expenses,
80:     net_amount,
81:     cumulative_net,
82:     region,
83:     department,
84:     project,
85:     current_timestamp AS report_generated_at
86: FROM with_cumulative
87: ORDER BY
88:     report_month DESC,
89:     CASE pl_category WHEN 'Revenue' THEN 1 WHEN 'Expenses' THEN 2 ELSE 3 END,
90:     account_code ASC
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/sql/marts/xero__profit_and_loss_report.sql`；SHA-256 `b35c54500c998d6012bc75c5b8cdaa01b166f009bb21c314c0abbe4a9df8abb0`。

```text
1: -- Mart table: Profit and Loss Report - show income and expenses over time
2: 
3: WITH general_ledger AS (
4:     SELECT
5:         journal_date,
6:         account_code,
7:         account_name,
8:         account_type,
9:         account_class,
10:         net_amount,
11: 
12:         CAST(EXTRACT(YEAR FROM CAST(journal_date AS DATE)) AS INT) AS fiscal_year,
13:         CAST(EXTRACT(MONTH FROM CAST(journal_date AS DATE)) AS INT) AS fiscal_month,
14:         EXTRACT(QUARTER FROM CAST(journal_date AS DATE)) AS fiscal_quarter,
15: 
16:         region,
17:         department,
18:         project,
19:         customer
20:     FROM intermediate.int_xero__general_ledger_fact
21: ),
22: 
23: profit_and_loss_data AS (
24:     SELECT
25:         journal_date,
26:         fiscal_year,
27:         fiscal_month,
28:         fiscal_quarter,
29:         account_code,
30:         account_name,
31:         account_type,
32:         account_class,
33: 
34:         -- Split out revenue and expenses (and other account types)
35:         CASE
36:             WHEN account_class = 'REVENUE' THEN net_amount
37:             ELSE 0
38:         END AS revenue_amount,
39: 
40:         CASE
41:             WHEN account_class = 'EXPENSE' THEN ABS(net_amount)  -- Make positive for expenses
42:             ELSE 0
43:         END AS expense_amount,
44: 
45:         net_amount AS net_amount,
46: 
47:         -- P&L classification
48:         CASE
49:             WHEN account_class = 'REVENUE' THEN 'Revenue'
50:             WHEN account_class = 'EXPENSE' THEN 'Expenses'
51:             WHEN account_class IN ('ASSET', 'LIABILITY', 'EQUITY') THEN 'Balance Sheet'
52:             ELSE 'Other'
53:         END AS pl_category,
54: 
55:         -- Detailed classification
56:         CASE
57:             WHEN account_type = 'REVENUE' THEN 'Operating Revenue'
58:             WHEN account_type = 'EXPENSE' AND CAST(account_code AS VARCHAR) LIKE '4%' THEN 'Operating Expenses'
59:             WHEN account_type = 'EXPENSE' AND CAST(account_code AS VARCHAR) LIKE '6%' THEN 'Administrative Expenses'
60:             WHEN account_type = 'DIRECTCOSTS' THEN 'Cost of Goods Sold'
61:             WHEN account_type = 'OVERHEADS' THEN 'Overhead'
62:             WHEN account_type = 'DEPRECIATN' THEN 'Depreciation'
63:             ELSE 'Other'
64:         END AS pl_subcategory,
65: 
66:         region,
67:         department,
68:         project,
69:         customer
70: 
71:     FROM general_ledger
72: ),
73: 
74: -- Aggregate by different time periods and dimensions
75: monthly_summary AS (
76:     SELECT
77:         DATE_TRUNC('MONTH', CAST(journal_date AS DATE)) AS report_month,
78:         fiscal_year,
79:         fiscal_month,
80:         fiscal_quarter,
81:         account_code,
82:         account_name,
83:         pl_category,
84:         pl_subcategory,
85:         region,
86:         department,
87:         project,
88: 
89:         SUM(revenue_amount) AS monthly_revenue,
90:         SUM(expense_amount) AS monthly_expenses,
91:         SUM(net_amount) AS monthly_net
92: 
93:     FROM profit_and_loss_data
94:     GROUP BY
95:         DATE_TRUNC('MONTH', CAST(journal_date AS DATE)),
96:         fiscal_year,
97:         fiscal_month,
98:         fiscal_quarter,
99:         account_code,
100:         account_name,
101:         pl_category,
102:         pl_subcategory,
103:         region,
104:         department,
105:         project
106: ),
107: 
108: quarterly_summary AS (
109:     SELECT
110:         DATE_TRUNC('QUARTER', report_month) AS report_quarter,
111:         fiscal_year,
112:         fiscal_quarter,
113:         pl_category,
114:         pl_subcategory,
115:         region,
116:         department,
117:         project,
118: 
119:         SUM(monthly_revenue) AS quarterly_revenue,
120:         SUM(monthly_expenses) AS quarterly_expenses,
121:         SUM(monthly_net) AS quarterly_net
122: 
123:     FROM monthly_summary
124:     GROUP BY
125:         DATE_TRUNC('QUARTER', report_month),
126:         fiscal_year,
127:         fiscal_quarter,
128:         pl_category,
129:         pl_subcategory,
130:         region,
131:         department,
132:         project
133: )
134: 
135: -- Final result with both detailed and summary views
136: SELECT
137:     report_month,
138:     fiscal_year,
139:     fiscal_month,
140:     'Monthly' AS period_type,
141:     pl_category,
142:     pl_subcategory,
143:     account_code,
144:     account_name,
145:     monthly_revenue AS revenue,
146:     monthly_expenses AS expenses,
147:     monthly_net AS net_amount,
148: 
149:     -- Running totals and percentages
150:     SUM(monthly_net) OVER (PARTITION BY report_month ORDER BY pl_category, account_code) AS cumulative_net,
151: 
152:     -- Tracking dimensions
153:     region,
154:     department,
155:     project,
156: 
157:     CURRENT_TIMESTAMP AS report_generated_at
158: 
159: FROM monthly_summary
160: WHERE monthly_revenue != 0 OR monthly_expenses != 0  -- Only show accounts with activity
161: 
162: ORDER BY
163:     report_month DESC,
164:     CASE pl_category
165:         WHEN 'Revenue' THEN 1
166:         WHEN 'Expenses' THEN 2
167:         ELSE 3
168:     END,
169:     account_code
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- 本表主要差异（O）：**看到了但没提**；事件 23、39。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。
event 23：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/23.json`；命令首行：`cat >> /tmp/models.py <<'PY'`。
event 39：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/39.json`；命令首行：`cat > result.md <<'EOF'`。

最终报告原文（用于复核说明和工作清单边界）：

```
【回复用户】

Implemented the Xero SQL pipeline in `sql/`, following the staging → intermediate → marts order and the provided data contract.

- Created 14 staging models, 5 intermediate models, and 4 marts models with DuckDB SQL, fully qualified upstream references, and no trailing semicolons.
- Applied contract-driven field cleaning, casting, and row filters; active-option matching and tracking pivots; invoice and general-ledger enrichment; and financial reporting calculations.
- Avoided duplicate account-code join expansion by selecting one account row per code. Duplicate source relationships remain preserved in the relationship model as contracted; pivots collapse repeated assignments and select the lexicographically greatest valid option.
- Validation results: invoice-line enriched and mart models each have 5,000 rows and 5,000 unique line-item IDs; the general ledger has 8,000 unique journal/journal-line combinations; staged invoices have 3,489 valid dates and no dates beyond the allowed horizon; no staged invoice unit amounts violate the defined range; and two of 22 tracking categories normalize to `UNKNOWN`.

Validation: `python run.py` completed successfully with all 14 staging, 5 intermediate, and 4 marts models created. Sanity checks verified unique IDs/keys and nonnegative invoice-level aggregates. No SQL execution failures remained.

Contract assumptions: Raw data does not provide a processing timestamp for some entities, so `processed_at` is NULL where unavailable. Available source timestamp strings are parsed with DuckDB `TRY_CAST`; invalid timestamps become NULL. General-ledger fact and report timestamps use `current_timestamp`. Duplicate account codes exist in source; the invoice enrichment chooses one account deterministically by lowest `account_id` to prevent duplicate output line rows. This can discard alternate account attributes for colliding codes.
```

## 查询

核实查询 **0** 条；代价档：**需要查业务说明**。含失败后重试的每条SQL；诊断查询不计入5条上限。

### 诊断：排除并列顺序派生列后的整表诊断
[024_extra_diagnostics.json](../024_extra_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/xero.duckdb`。

```sql
WITH journal_lines AS (
    SELECT
        TRY_CAST(journal_date AS DATE) AS journal_date,
        account_class,
        account_type,
        account_code,
        account_name,
        net_amount,
        region,
        department,
        project,
        CASE WHEN account_class = 'REVENUE' THEN net_amount ELSE 0 END AS revenue_amount,
        CASE WHEN account_class = 'EXPENSE' THEN abs(net_amount) ELSE 0 END AS expense_amount,
        CASE
            WHEN account_class = 'REVENUE' THEN 'Revenue'
            WHEN account_class = 'EXPENSE' THEN 'Expenses'
            WHEN account_class IN ('ASSET', 'LIABILITY', 'EQUITY') THEN 'Balance Sheet'
            ELSE 'Other'
        END AS pl_category,
        CASE
            WHEN account_type = 'REVENUE' THEN 'Operating Revenue'
            WHEN account_type = 'EXPENSE' AND starts_with(CAST(account_code AS VARCHAR), '4') THEN 'Operating Expenses'
            WHEN account_type = 'EXPENSE' AND starts_with(CAST(account_code AS VARCHAR), '6') THEN 'Administrative Expenses'
            WHEN account_type = 'DIRECTCOSTS' THEN 'Cost of Goods Sold'
            WHEN account_type = 'OVERHEADS' THEN 'Overhead'
            WHEN account_type = 'DEPRECIATN' THEN 'Depreciation'
            ELSE 'Other'
        END AS pl_subcategory
    FROM intermediate.int_xero__general_ledger_fact
    WHERE journal_date IS NOT NULL
),
monthly AS (
    SELECT
        date_trunc('month', journal_date)::DATE AS report_month,
        year(journal_date)::INTEGER AS fiscal_year,
        month(journal_date)::INTEGER AS fiscal_month,
        quarter(journal_date)::INTEGER AS fiscal_quarter,
        account_code,
        account_name,
        pl_category,
        pl_subcategory,
        region,
        department,
        project,
        sum(revenue_amount)::DOUBLE AS revenue,
        sum(expense_amount)::DOUBLE AS expenses,
        sum(net_amount)::DOUBLE AS net_amount
    FROM journal_lines
    GROUP BY
        report_month, fiscal_year, fiscal_month, fiscal_quarter,
        account_code, account_name, pl_category, pl_subcategory,
        region, department, project
),
filtered AS (
    SELECT *
    FROM monthly
    WHERE revenue <> 0 OR expenses <> 0
),
with_cumulative AS (
    SELECT
        *,
        sum(net_amount) OVER (
            PARTITION BY report_month
            ORDER BY pl_category ASC, account_code ASC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_net
    FROM filtered
)
SELECT
    report_month,
    fiscal_year,
    fiscal_month,
    'Monthly' AS period_type,
    pl_category,
    pl_subcategory,
    account_code,
    account_name,
    revenue,
    expenses,
    net_amount,
    cumulative_net,
    region,
    department,
    project,
    TIMESTAMPTZ '2025-10-17 11:30:25.438839+08:00' AS report_generated_at
FROM with_cumulative
ORDER BY
    report_month DESC,
    CASE pl_category WHEN 'Revenue' THEN 1 WHEN 'Expenses' THEN 2 ELSE 3 END,
    account_code ASC
```

|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1657|1657|0|0|是|
|L1|1657|1657|0|0|是|
|L2|1657|1657|0|0|是|
|L3|1657|1657|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`
excluded：`["cumulative_net"]`
tie_groups：`{"sql":"SELECT count(*) FROM (SELECT report_month,pl_category,account_code FROM pred GROUP BY ALL HAVING count(*)>1)","count":8}`

### 诊断：gold SQL同gold输入重跑
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/xero.duckdb`。

```sql
-- Mart table: Profit and Loss Report - show income and expenses over time

WITH general_ledger AS (
    SELECT
        journal_date,
        account_code,
        account_name,
        account_type,
        account_class,
        net_amount,

        CAST(EXTRACT(YEAR FROM CAST(journal_date AS DATE)) AS INT) AS fiscal_year,
        CAST(EXTRACT(MONTH FROM CAST(journal_date AS DATE)) AS INT) AS fiscal_month,
        EXTRACT(QUARTER FROM CAST(journal_date AS DATE)) AS fiscal_quarter,

        region,
        department,
        project,
        customer
    FROM intermediate.int_xero__general_ledger_fact
),

profit_and_loss_data AS (
    SELECT
        journal_date,
        fiscal_year,
        fiscal_month,
        fiscal_quarter,
        account_code,
        account_name,
        account_type,
        account_class,

        -- Split out revenue and expenses (and other account types)
        CASE
            WHEN account_class = 'REVENUE' THEN net_amount
            ELSE 0
        END AS revenue_amount,

        CASE
            WHEN account_class = 'EXPENSE' THEN ABS(net_amount)  -- Make positive for expenses
            ELSE 0
        END AS expense_amount,

        net_amount AS net_amount,

        -- P&L classification
        CASE
            WHEN account_class = 'REVENUE' THEN 'Revenue'
            WHEN account_class = 'EXPENSE' THEN 'Expenses'
            WHEN account_class IN ('ASSET', 'LIABILITY', 'EQUITY') THEN 'Balance Sheet'
            ELSE 'Other'
        END AS pl_category,

        -- Detailed classification
        CASE
            WHEN account_type = 'REVENUE' THEN 'Operating Revenue'
            WHEN account_type = 'EXPENSE' AND CAST(account_code AS VARCHAR) LIKE '4%' THEN 'Operating Expenses'
            WHEN account_type = 'EXPENSE' AND CAST(account_code AS VARCHAR) LIKE '6%' THEN 'Administrative Expenses'
            WHEN account_type = 'DIRECTCOSTS' THEN 'Cost of Goods Sold'
            WHEN account_type = 'OVERHEADS' THEN 'Overhead'
            WHEN account_type = 'DEPRECIATN' THEN 'Depreciation'
            ELSE 'Other'
        END AS pl_subcategory,

        region,
        department,
        project,
        customer

    FROM general_ledger
),

-- Aggregate by different time periods and dimensions
monthly_summary AS (
    SELECT
        DATE_TRUNC('MONTH', CAST(journal_date AS DATE)) AS report_month,
        fiscal_year,
        fiscal_month,
        fiscal_quarter,
        account_code,
        account_name,
        pl_category,
        pl_subcategory,
        region,
        department,
        project,

        SUM(revenue_amount) AS monthly_revenue,
        SUM(expense_amount) AS monthly_expenses,
        SUM(net_amount) AS monthly_net

    FROM profit_and_loss_data
    GROUP BY
        DATE_TRUNC('MONTH', CAST(journal_date AS DATE)),
        fiscal_year,
        fiscal_month,
        fiscal_quarter,
        account_code,
        account_name,
        pl_category,
        pl_subcategory,
        region,
        department,
        project
),

quarterly_summary AS (
    SELECT
        DATE_TRUNC('QUARTER', report_month) AS report_quarter,
        fiscal_year,
        fiscal_quarter,
        pl_category,
        pl_subcategory,
        region,
        department,
        project,

        SUM(monthly_revenue) AS quarterly_revenue,
        SUM(monthly_expenses) AS quarterly_expenses,
        SUM(monthly_net) AS quarterly_net

    FROM monthly_summary
    GROUP BY
        DATE_TRUNC('QUARTER', report_month),
        fiscal_year,
        fiscal_quarter,
        pl_category,
        pl_subcategory,
        region,
        department,
        project
)

-- Final result with both detailed and summary views
SELECT
    report_month,
    fiscal_year,
    fiscal_month,
    'Monthly' AS period_type,
    pl_category,
    pl_subcategory,
    account_code,
    account_name,
    monthly_revenue AS revenue,
    monthly_expenses AS expenses,
    monthly_net AS net_amount,

    -- Running totals and percentages
    SUM(monthly_net) OVER (PARTITION BY report_month ORDER BY pl_category, account_code) AS cumulative_net,

    -- Tracking dimensions
    region,
    department,
    project,

    TIMESTAMPTZ '2025-10-17 11:30:25.438839+08:00' AS report_generated_at

FROM monthly_summary
WHERE monthly_revenue != 0 OR monthly_expenses != 0  -- Only show accounts with activity

ORDER BY
    report_month DESC,
    CASE pl_category
        WHEN 'Revenue' THEN 1
        WHEN 'Expenses' THEN 2
        ELSE 3
    END,
    account_code
```

|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1657|1657|266|266|否|
|L1|1657|1657|266|266|否|
|L2|1657|1657|0|0|是|
|L3|1657|1657|0|0|是|

首次整表匹配：**L2**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"cumulative_net":266}`
- L1：`{"cumulative_net":266}`
- L2：`{}`
- L3：`{}`

### 诊断：固定时间
[024_history_clock.json](../024_history_clock.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/xero.duckdb`。

```sql
SELECT min(report_generated_at),max(report_generated_at) FROM marts.xero__profit_and_loss_report
```


```json
{"rows":[["2025-10-17 11:30:25.438839+08:00","2025-10-17 11:30:25.438839+08:00"]]}
```

## 独立单点重跑

### 024_reruns_impl-027_xero__profit_and_loss_report.json
[024_reruns_impl-027_xero__profit_and_loss_report.json](../024_reruns_impl-027_xero__profit_and_loss_report.json)
上游：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-027/xero.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-17 11:30:25.438839+08:00'","count":1},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-17'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1657|1657|8|16|否|
|L1|1657|1657|8|8|否|
|L2|1657|1657|8|8|否|
|L3|1657|1657|8|8|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"cumulative_net":8,"fiscal_month":2,"fiscal_year":2,"net_amount":2,"revenue":2}`
- L1：`{"cumulative_net":8}`
- L2：`{"cumulative_net":8}`
- L3：`{"cumulative_net":8}`

#### baseline
私有SQL：`data/024_work/impl-027_xero__profit_and_loss_report/baseline.sql`；SHA-256 `42cd6e5f505dfedfd5784ecd04ada6d55b4e2e1814706597879477c48990cdb0`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1657|1657|11|11|否|
|L1|1657|1657|11|11|否|
|L2|1657|1657|8|8|否|
|L3|1657|1657|8|8|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"cumulative_net":11}`
- L1：`{"cumulative_net":11}`
- L2：`{"cumulative_net":8}`
- L3：`{"cumulative_net":8}`

#### window_frame
不计参与因素；类别候选O。契约允许并列项任意序，但gold默认RANGE同键整组累加；agent ROWS逐行累加。需诊断其余内容一致。
相对本轮基线：行减少8，格减少8。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第65行、offset 2385起替换；其他字节相同。
原表达式：
```sql
ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
```

修改后：
```sql
RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
```

私有SQL：`data/024_work/impl-027_xero__profit_and_loss_report/window_frame.sql`；SHA-256 `c11748fd286263568994d39be2153dc57a634079eba1b7231c92c975e87a98eb`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1657|1657|3|3|否|
|L1|1657|1657|3|3|否|
|L2|1657|1657|0|0|是|
|L3|1657|1657|0|0|是|

首次整表匹配：**L2**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"cumulative_net":3}`
- L1：`{"cumulative_net":3}`
- L2：`{}`
- L3：`{}`
## 规则问题

ROWS逐行任意序与RANGE整组累计并非单纯重排，但契约描述running total且ties nondeterministic支持agent；按gold与契约行为冲突归O，另浮点差异L2消失。

