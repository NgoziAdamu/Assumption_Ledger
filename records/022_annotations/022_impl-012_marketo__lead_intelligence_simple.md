# impl-012 / marketo__lead_intelligence_simple（全量；v2）

## 1. 差异与结论

无邮件发送的376个lead在rfm_segment和next_best_action各有一处差异。前者违背明确Unknown默认；后者agent按“无打开→Welcome Series”，gold对缺失聚合的NULL落到Standard Campaign Flow。两项单修行数不变、各减376格，C/O并列。

主要原因：**多因并列**；参与因素：无；把握：中；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**格子**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| missing_segment | C | 0 | 376 |
| missing_action | O | 0 | 376 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-012_marketo__lead_intelligence_simple.md](../../records/022_packages/022_impl-012_marketo__lead_intelligence_simple.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-012_marketo__lead_intelligence_simple/022_impl-012_marketo__lead_intelligence_simple.json`。
- 比较结果：[022_reruns_impl-012_marketo__lead_intelligence_simple.json](../022_reruns_impl-012_marketo__lead_intelligence_simple.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-012/docs/data_contract.yaml`。

原件第1457–1579行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/sql/marts/marketo__lead_intelligence_simple.sql`；原件第1–1行。

```sql
   1: WITH lead_base AS (SELECT lead_id,email,first_name,last_name,created_timestamp,updated_timestamp FROM intermediate.int_marketo__lead WHERE NOT is_deleted AND NOT is_merged), engagement AS (SELECT lead_id,COUNT(*)::BIGINT AS total_emails_sent,COUNT(*) FILTER(WHERE was_opened)::BIGINT AS total_emails_opened,COUNT(*) FILTER(WHERE was_clicked)::BIGINT AS total_emails_clicked,COUNT(*) FILTER(WHERE was_bounced)::BIGINT AS total_emails_bounced,COUNT(*) FILTER(WHERE was_unsubscribed)::BIGINT AS total_unsubscribes,COUNT(DISTINCT campaign_id)::BIGINT AS unique_campaigns_participated,MIN(activity_timestamp) AS first_email_sent_at,MAX(activity_timestamp) AS last_email_sent_at,MAX(activity_timestamp) FILTER(WHERE was_opened) AS last_email_opened_at,MAX(activity_timestamp) FILTER(WHERE was_clicked) AS last_email_clicked_at FROM marts.marketo__email_sends WHERE lead_id IS NOT NULL GROUP BY lead_id), metrics AS (SELECT l.*,COALESCE(e.total_emails_sent,0)::BIGINT AS total_emails_sent,COALESCE(e.total_emails_opened,0)::BIGINT AS total_emails_opened,COALESCE(e.total_emails_clicked,0)::BIGINT AS total_emails_clicked,COALESCE(e.total_emails_bounced,0)::BIGINT AS total_emails_bounced,COALESCE(e.total_unsubscribes,0)::BIGINT AS total_unsubscribes,COALESCE(e.unique_campaigns_participated,0)::BIGINT AS unique_campaigns_participated,e.first_email_sent_at,e.last_email_sent_at,e.last_email_opened_at,e.last_email_clicked_at,CASE WHEN COALESCE(e.total_emails_sent,0)=0 THEN 0 ELSE ROUND(e.total_emails_opened::DOUBLE/e.total_emails_sent*100,2) END AS email_open_rate_pct,CASE WHEN COALESCE(e.total_emails_sent,0)=0 THEN 0 ELSE ROUND(e.total_emails_clicked::DOUBLE/e.total_emails_sent*100,2) END AS email_click_rate_pct,COALESCE(e.total_emails_opened,0)*5+COALESCE(e.total_emails_clicked,0)*10 AS total_lead_score FROM lead_base l LEFT JOIN engagement e USING(lead_id)), segmented AS (SELECT *,CASE WHEN total_lead_score>=100 THEN 'Champion' WHEN total_lead_score>=50 THEN 'Loyal Customer' WHEN total_lead_score>=25 THEN 'Potential Loyalist' WHEN total_lead_score>=10 THEN 'Regular Subscriber' WHEN total_lead_score>=5 THEN 'At Risk' ELSE 'Inactive' END AS rfm_segment,CASE WHEN total_lead_score>=80 THEN 'Platinum' WHEN total_lead_score>=50 THEN 'Gold' WHEN total_lead_score>=25 THEN 'Silver' WHEN total_lead_score>=10 THEN 'Bronze' ELSE 'Basic' END AS value_tier,CASE WHEN email_open_rate_pct>=50 AND email_click_rate_pct>=10 THEN 'A-Tier' WHEN email_open_rate_pct>=30 AND email_click_rate_pct>=5 THEN 'B-Tier' WHEN email_open_rate_pct>=15 THEN 'C-Tier' WHEN email_open_rate_pct>=5 THEN 'D-Tier' ELSE 'Unqualified' END AS lead_quality_tier FROM metrics) SELECT lead_id,email,first_name,last_name,created_timestamp AS lead_created_at,total_emails_sent,total_emails_opened,total_emails_clicked,total_emails_bounced,total_unsubscribes,unique_campaigns_participated,email_open_rate_pct,email_click_rate_pct,total_lead_score,first_email_sent_at,last_email_sent_at,last_email_opened_at,last_email_clicked_at,COALESCE(DATE_DIFF('day',CAST(last_email_sent_at AS DATE),CURRENT_DATE),9999)::BIGINT AS days_since_last_email,COALESCE(DATE_DIFF('day',CAST(last_email_opened_at AS DATE),CURRENT_DATE),9999)::BIGINT AS days_since_last_open,COALESCE(DATE_DIFF('day',CAST(last_email_clicked_at AS DATE),CURRENT_DATE),9999)::BIGINT AS days_since_last_click,rfm_segment,value_tier,lead_quality_tier,COALESCE(DATE_DIFF('day',TRY_CAST(SUBSTR(created_timestamp,1,10) AS DATE),CURRENT_DATE),0)::BIGINT AS lead_tenure_days,CASE WHEN total_lead_score>=50 AND COALESCE(DATE_DIFF('day',CAST(last_email_opened_at AS DATE),CURRENT_DATE),9999)<=30 THEN 'Healthy' WHEN total_lead_score>=25 AND COALESCE(DATE_DIFF('day',CAST(last_email_opened_at AS DATE),CURRENT_DATE),9999)<=60 THEN 'Good' WHEN total_lead_score>=10 AND COALESCE(DATE_DIFF('day',CAST(last_email_opened_at AS DATE),CURRENT_DATE),9999)<=90 THEN 'Fair' WHEN total_lead_score>=5 THEN 'Poor' ELSE 'Critical' END AS lead_health_status,CASE WHEN email_click_rate_pct>=10 AND COALESCE(DATE_DIFF('day',CAST(last_email_clicked_at AS DATE),CURRENT_DATE),9999)<=7 THEN 'Schedule Sales Call' WHEN email_open_rate_pct>=30 THEN 'Send Product Demo' WHEN days_since_last_open>60 AND total_emails_opened>0 THEN 'Re-engagement Campaign' WHEN total_emails_opened=0 THEN 'Welcome Series' ELSE 'Standard Campaign Flow' END AS next_best_action,CURRENT_TIMESTAMP AS last_updated_at FROM (SELECT *,COALESCE(DATE_DIFF('day',CAST(last_email_opened_at AS DATE),CURRENT_DATE),9999) AS days_since_last_open FROM segmented) final_rows
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-012/sql/marts/marketo__lead_intelligence_simple.sql`；原件第1–171行。

```sql
   1: -- Marts: Simplified lead intelligence dashboard
   2: 
   3: WITH lead_base AS (
   4:     SELECT 
   5:         lead_id,
   6:         email,
   7:         first_name,
   8:         last_name,
   9:         created_timestamp,
  10:         updated_timestamp,
  11:         is_deleted,
  12:         is_merged
  13:     FROM intermediate.int_marketo__lead
  14:     WHERE NOT is_deleted AND NOT is_merged
  15: ),
  16: 
  17: -- Email engagement metrics per lead
  18: email_engagement AS (
  19:     SELECT 
  20:         lead_id,
  21:         COUNT(*) as total_emails_sent,
  22:         COUNT(CASE WHEN was_opened THEN 1 END) as total_emails_opened,
  23:         COUNT(CASE WHEN was_clicked THEN 1 END) as total_emails_clicked,
  24:         COUNT(CASE WHEN was_bounced THEN 1 END) as total_emails_bounced,
  25:         COUNT(CASE WHEN was_unsubscribed THEN 1 END) as total_unsubscribes,
  26:         COUNT(DISTINCT email_template_id) as unique_email_templates_received,
  27:         COUNT(DISTINCT campaign_id) as unique_campaigns_participated,
  28:         MAX(activity_timestamp) as last_email_sent_at,
  29:         MAX(CASE WHEN was_opened THEN activity_timestamp END) as last_email_opened_at,
  30:         MAX(CASE WHEN was_clicked THEN activity_timestamp END) as last_email_clicked_at,
  31:         MIN(activity_timestamp) as first_email_sent_at,
  32:         
  33:         -- Engagement rates
  34:         CASE 
  35:             WHEN COUNT(*) > 0 
  36:             THEN ROUND((COUNT(CASE WHEN was_opened THEN 1 END)::DOUBLE / COUNT(*)) * 100, 2)
  37:             ELSE 0 
  38:         END as email_open_rate_pct,
  39:         
  40:         CASE 
  41:             WHEN COUNT(*) > 0 
  42:             THEN ROUND((COUNT(CASE WHEN was_clicked THEN 1 END)::DOUBLE / COUNT(*)) * 100, 2)
  43:             ELSE 0 
  44:         END as email_click_rate_pct,
  45:         
  46:         -- Simple lead scoring
  47:         COUNT(CASE WHEN was_opened THEN 1 END) * 5 + COUNT(CASE WHEN was_clicked THEN 1 END) * 10 as total_lead_score
  48:         
  49:     FROM marts.marketo__email_sends
  50:     WHERE lead_id IS NOT NULL
  51:     GROUP BY lead_id
  52: ),
  53: 
  54: -- Lead segmentation
  55: lead_segmentation AS (
  56:     SELECT 
  57:         lead_id,
  58:         -- Behavioral segmentation based on engagement
  59:         CASE 
  60:             WHEN total_lead_score >= 100 THEN 'Champion'
  61:             WHEN total_lead_score >= 50 THEN 'Loyal Customer'
  62:             WHEN total_lead_score >= 25 THEN 'Potential Loyalist'
  63:             WHEN total_lead_score >= 10 THEN 'Regular Subscriber'
  64:             WHEN total_lead_score >= 5 THEN 'At Risk'
  65:             ELSE 'Inactive'
  66:         END as rfm_segment,
  67:         
  68:         -- Value tier
  69:         CASE 
  70:             WHEN total_lead_score >= 80 THEN 'Platinum'
  71:             WHEN total_lead_score >= 50 THEN 'Gold'
  72:             WHEN total_lead_score >= 25 THEN 'Silver'
  73:             WHEN total_lead_score >= 10 THEN 'Bronze'
  74:             ELSE 'Basic'
  75:         END as value_tier,
  76:         
  77:         -- Lead quality based on engagement
  78:         CASE 
  79:             WHEN email_open_rate_pct >= 50 AND email_click_rate_pct >= 10 THEN 'A-Tier'
  80:             WHEN email_open_rate_pct >= 30 AND email_click_rate_pct >= 5 THEN 'B-Tier'
  81:             WHEN email_open_rate_pct >= 15 THEN 'C-Tier'
  82:             WHEN email_open_rate_pct >= 5 THEN 'D-Tier'
  83:             ELSE 'Unqualified'
  84:         END as lead_quality_tier
  85:         
  86:     FROM email_engagement
  87: ),
  88: 
  89: final AS (
  90:     SELECT 
  91:         lb.lead_id,
  92:         lb.email,
  93:         lb.first_name,
  94:         lb.last_name,
  95:         lb.created_timestamp as lead_created_at,
  96:         
  97:         -- Core metrics
  98:         COALESCE(ee.total_emails_sent, 0) as total_emails_sent,
  99:         COALESCE(ee.total_emails_opened, 0) as total_emails_opened,
 100:         COALESCE(ee.total_emails_clicked, 0) as total_emails_clicked,
 101:         COALESCE(ee.total_emails_bounced, 0) as total_emails_bounced,
 102:         COALESCE(ee.total_unsubscribes, 0) as total_unsubscribes,
 103:         COALESCE(ee.unique_campaigns_participated, 0) as unique_campaigns_participated,
 104:         
 105:         -- Engagement rates  
 106:         COALESCE(ee.email_open_rate_pct, 0) as email_open_rate_pct,
 107:         COALESCE(ee.email_click_rate_pct, 0) as email_click_rate_pct,
 108:         
 109:         -- Lead scoring
 110:         COALESCE(ee.total_lead_score, 0) as total_lead_score,
 111:         
 112:         -- Timing insights
 113:         ee.first_email_sent_at,
 114:         ee.last_email_sent_at,
 115:         ee.last_email_opened_at,
 116:         ee.last_email_clicked_at,
 117:         
 118:         -- Days since activities
 119:         CASE 
 120:             WHEN ee.last_email_sent_at IS NOT NULL 
 121:             THEN DATE_DIFF('day', CAST(ee.last_email_sent_at AS DATE), CURRENT_DATE)
 122:             ELSE 9999 
 123:         END as days_since_last_email,
 124:         
 125:         CASE 
 126:             WHEN ee.last_email_opened_at IS NOT NULL 
 127:             THEN DATE_DIFF('day', CAST(ee.last_email_opened_at AS DATE), CURRENT_DATE)
 128:             ELSE 9999 
 129:         END as days_since_last_open,
 130:         
 131:         CASE 
 132:             WHEN ee.last_email_clicked_at IS NOT NULL 
 133:             THEN DATE_DIFF('day', CAST(ee.last_email_clicked_at AS DATE), CURRENT_DATE)
 134:             ELSE 9999 
 135:         END as days_since_last_click,
 136:         
 137:         -- Segmentation
 138:         COALESCE(ls.rfm_segment, 'Unknown') as rfm_segment,
 139:         COALESCE(ls.value_tier, 'Basic') as value_tier,
 140:         COALESCE(ls.lead_quality_tier, 'Unqualified') as lead_quality_tier,
 141:         
 142:         -- Lead tenure
 143:         DATE_DIFF('day', CAST(lb.created_timestamp AS DATE), CURRENT_DATE) as lead_tenure_days,
 144:         
 145:         -- Lead health status
 146:         CASE 
 147:             WHEN ee.total_lead_score >= 50 AND DATE_DIFF('day', CAST(ee.last_email_opened_at AS DATE), CURRENT_DATE) <= 30 THEN 'Healthy'
 148:             WHEN ee.total_lead_score >= 25 AND DATE_DIFF('day', CAST(ee.last_email_opened_at AS DATE), CURRENT_DATE) <= 60 THEN 'Good'
 149:             WHEN ee.total_lead_score >= 10 AND DATE_DIFF('day', CAST(ee.last_email_opened_at AS DATE), CURRENT_DATE) <= 90 THEN 'Fair'
 150:             WHEN ee.total_lead_score >= 5 THEN 'Poor'
 151:             ELSE 'Critical'
 152:         END as lead_health_status,
 153:         
 154:         -- Next best action
 155:         CASE 
 156:             WHEN ee.email_click_rate_pct >= 10 AND DATE_DIFF('day', CAST(ee.last_email_clicked_at AS DATE), CURRENT_DATE) <= 7 THEN 'Schedule Sales Call'
 157:             WHEN ee.email_open_rate_pct >= 30 THEN 'Send Product Demo'
 158:             WHEN DATE_DIFF('day', CAST(ee.last_email_opened_at AS DATE), CURRENT_DATE) > 60 AND ee.total_emails_opened > 0 THEN 'Re-engagement Campaign'
 159:             WHEN ee.total_emails_opened = 0 THEN 'Welcome Series'
 160:             ELSE 'Standard Campaign Flow'
 161:         END as next_best_action,
 162:         
 163:         CURRENT_TIMESTAMP as last_updated_at
 164:         
 165:     FROM lead_base lb
 166:     LEFT JOIN email_engagement ee ON lb.lead_id = ee.lead_id
 167:     LEFT JOIN lead_segmentation ls ON lb.lead_id = ls.lead_id
 168: )
 169: 
 170: SELECT *
 171: FROM final
```

## 3. agent看到的材料与不确定性

已检视该题全部57个原始归档事件（原输出显式截断事件：[]），最终报告与写报告动作。程序读取YAML不等于把完整YAML显示给agent；不推断未留存思考。

- event 45 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/45.json`。
- event 46 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/46.json`。

四档：**看到了但没提**。

| 并列项 | 四档 |
|---|---|
| missing_segment | 看到了但没提 |
| missing_action | 看到了但没提 |

未找到针对本表主项选择的说明。“看到了但没提”只表示上述实际输出包含相关schema、样例、代码/运行结果；不把写SQL本身或通用功能清单当作具体说明。“没有迹象”不推断agent内部没有意识到。

## 4. 核实查询与诊断

核实查询共**2条**（含失败尝试），代价档：**多条查询**，≤5；只查agent当时可见库。原始库READ_ONLY；所有写表在data/022_work等私有目录。

### 核实 V1：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/marketo.duckdb`。

```sql
SELECT 'intermediate.int_marketo__lead' source_table,count(*) rows FROM intermediate.int_marketo__lead UNION ALL SELECT 'marts.marketo__email_sends' source_table,count(*) rows FROM marts.marketo__email_sends
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: ... 'intermediate.int_marketo__lead' source_table,count(*) rows FROM intermediate.int_marketo__lead UNION ALL SELECT...\n                                                                   ^"}
```

### 核实 V2：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/marketo.duckdb`。

```sql
SELECT 'intermediate.int_marketo__lead' source_table,count(*) source_rows FROM intermediate.int_marketo__lead UNION ALL SELECT 'marts.marketo__email_sends' source_table,count(*) source_rows FROM marts.marketo__email_sends
```

```json
{"columns": ["source_table", "source_rows"], "result": [["intermediate.int_marketo__lead", 5984], ["marts.marketo__email_sends", 15000]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-012/marketo.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 9}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["lead_id"]`；比较列：`["days_since_last_email", "email", "email_open_rate_pct", "first_name", "last_name", "lead_health_status", "lead_id", "lead_quality_tier", "lead_tenure_days", "next_best_action", "rfm_segment", "total_emails_bounced", "total_emails_clicked", "total_emails_opened", "total_emails_sent", "total_lead_score", "total_unsubscribes", "unique_campaigns_participated", "value_tier"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 4823/4823 | 0/0 | 0/0 | 376 | 376 | 752 | False |
| L1 | 4823/4823 | 0/0 | 0/0 | 376 | 376 | 752 | False |
| L2 | 4823/4823 | 0/0 | 0/0 | 376 | 376 | 752 | False |
| L3 | 4823/4823 | 0/0 | 0/0 | 376 | 376 | 752 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| lead_id | 0 | 0 | 0 | 0 |
| days_since_last_email | 0 | 0 | 0 | 0 |
| email | 0 | 0 | 0 | 0 |
| email_open_rate_pct | 0 | 0 | 0 | 0 |
| first_name | 0 | 0 | 0 | 0 |
| last_name | 0 | 0 | 0 | 0 |
| lead_health_status | 0 | 0 | 0 | 0 |
| lead_quality_tier | 0 | 0 | 0 | 0 |
| lead_tenure_days | 0 | 0 | 0 | 0 |
| next_best_action | 376 | 376 | 376 | 376 |
| rfm_segment | 376 | 376 | 376 | 376 |
| total_emails_bounced | 0 | 0 | 0 | 0 |
| total_emails_clicked | 0 | 0 | 0 | 0 |
| total_emails_opened | 0 | 0 | 0 | 0 |
| total_emails_sent | 0 | 0 | 0 | 0 |
| total_lead_score | 0 | 0 | 0 | 0 |
| total_unsubscribes | 0 | 0 | 0 | 0 |
| unique_campaigns_participated | 0 | 0 | 0 | 0 |
| value_tier | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-012_marketo__lead_intelligence_simple/baseline.sql`；SHA-256：`c2cfce01e886a6c4b98eacf3227dd303aee09338b44da401b8b0da51d0b6e988`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 4823/4823 | 0/0 | 0/0 | 376 | 376 | 752 | False |
| L1 | 4823/4823 | 0/0 | 0/0 | 376 | 376 | 752 | False |
| L2 | 4823/4823 | 0/0 | 0/0 | 376 | 376 | 752 | False |
| L3 | 4823/4823 | 0/0 | 0/0 | 376 | 376 | 752 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| lead_id | 0 | 0 | 0 | 0 |
| days_since_last_email | 0 | 0 | 0 | 0 |
| email | 0 | 0 | 0 | 0 |
| email_open_rate_pct | 0 | 0 | 0 | 0 |
| first_name | 0 | 0 | 0 | 0 |
| last_name | 0 | 0 | 0 | 0 |
| lead_health_status | 0 | 0 | 0 | 0 |
| lead_quality_tier | 0 | 0 | 0 | 0 |
| lead_tenure_days | 0 | 0 | 0 | 0 |
| next_best_action | 376 | 376 | 376 | 376 |
| rfm_segment | 376 | 376 | 376 | 376 |
| total_emails_bounced | 0 | 0 | 0 | 0 |
| total_emails_clicked | 0 | 0 | 0 | 0 |
| total_emails_opened | 0 | 0 | 0 | 0 |
| total_emails_sent | 0 | 0 | 0 | 0 |
| total_lead_score | 0 | 0 | 0 | 0 |
| total_unsubscribes | 0 | 0 | 0 | 0 |
| unique_campaigns_participated | 0 | 0 | 0 | 0 |
| value_tier | 0 | 0 | 0 | 0 |

### missing_segment

SQL：`data/022_work/impl-012_marketo__lead_intelligence_simple/missing_segment.sql`；SHA-256：`afdc5b62406527e05b336b891873790ec85ea9c4d711bdcaa55030f4564370b9`。

替换offset=1887，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CASE WHEN total_lead_score>=100
-- 新
CASE WHEN total_emails_sent=0 THEN 'Unknown' WHEN total_lead_score>=100
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 4823/4823 | 0/0 | 0/0 | 376 | 376 | 376 | False |
| L1 | 4823/4823 | 0/0 | 0/0 | 376 | 376 | 376 | False |
| L2 | 4823/4823 | 0/0 | 0/0 | 376 | 376 | 376 | False |
| L3 | 4823/4823 | 0/0 | 0/0 | 376 | 376 | 376 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| lead_id | 0 | 0 | 0 | 0 |
| days_since_last_email | 0 | 0 | 0 | 0 |
| email | 0 | 0 | 0 | 0 |
| email_open_rate_pct | 0 | 0 | 0 | 0 |
| first_name | 0 | 0 | 0 | 0 |
| last_name | 0 | 0 | 0 | 0 |
| lead_health_status | 0 | 0 | 0 | 0 |
| lead_quality_tier | 0 | 0 | 0 | 0 |
| lead_tenure_days | 0 | 0 | 0 | 0 |
| next_best_action | 376 | 376 | 376 | 376 |
| rfm_segment | 0 | 0 | 0 | 0 |
| total_emails_bounced | 0 | 0 | 0 | 0 |
| total_emails_clicked | 0 | 0 | 0 | 0 |
| total_emails_opened | 0 | 0 | 0 | 0 |
| total_emails_sent | 0 | 0 | 0 | 0 |
| total_lead_score | 0 | 0 | 0 | 0 |
| total_unsubscribes | 0 | 0 | 0 | 0 |
| unique_campaigns_participated | 0 | 0 | 0 | 0 |
| value_tier | 0 | 0 | 0 | 0 |

### missing_action

SQL：`data/022_work/impl-012_marketo__lead_intelligence_simple/missing_action.sql`；SHA-256：`5d8280bdd7cd3893815fb8adb25f9716ccee8ee48fe7164e04b5456aed13e778`。

替换offset=4288，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
WHEN total_emails_opened=0 THEN 'Welcome Series'
-- 新
WHEN total_emails_sent>0 AND total_emails_opened=0 THEN 'Welcome Series'
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 4823/4823 | 0/0 | 0/0 | 376 | 376 | 376 | False |
| L1 | 4823/4823 | 0/0 | 0/0 | 376 | 376 | 376 | False |
| L2 | 4823/4823 | 0/0 | 0/0 | 376 | 376 | 376 | False |
| L3 | 4823/4823 | 0/0 | 0/0 | 376 | 376 | 376 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| lead_id | 0 | 0 | 0 | 0 |
| days_since_last_email | 0 | 0 | 0 | 0 |
| email | 0 | 0 | 0 | 0 |
| email_open_rate_pct | 0 | 0 | 0 | 0 |
| first_name | 0 | 0 | 0 | 0 |
| last_name | 0 | 0 | 0 | 0 |
| lead_health_status | 0 | 0 | 0 | 0 |
| lead_quality_tier | 0 | 0 | 0 | 0 |
| lead_tenure_days | 0 | 0 | 0 | 0 |
| next_best_action | 0 | 0 | 0 | 0 |
| rfm_segment | 376 | 376 | 376 | 376 |
| total_emails_bounced | 0 | 0 | 0 | 0 |
| total_emails_clicked | 0 | 0 | 0 | 0 |
| total_emails_opened | 0 | 0 | 0 | 0 |
| total_emails_sent | 0 | 0 | 0 | 0 |
| total_lead_score | 0 | 0 | 0 | 0 |
| total_unsubscribes | 0 | 0 | 0 | 0 |
| unique_campaigns_participated | 0 | 0 | 0 | 0 |
| value_tier | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：missing_segment,missing_action；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- missing_segment：C；主项。契约无engagement时rfm_segment为Unknown；agent在补零后分段为Inactive。（行减少0，格减少376）
- missing_action：O；主项。契约无打开时Welcome Series；gold缺失engagement的NULL未命中0而给Standard Campaign Flow。（行减少0，格减少376）

## 规则问题

无。按v2冻结定义执行。
