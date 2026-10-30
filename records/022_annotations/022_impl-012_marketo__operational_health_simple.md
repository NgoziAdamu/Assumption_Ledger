# impl-012 / marketo__operational_health_simple（全量；v2）

## 1. 差异与结论

原评测时间戳键遮住payload。共同固定到gold留存时刻后仅health score和recommendation文案不同；契约没有给四项具体分值或完整文案，两项均A。

主要原因：**A**；参与因素：无；把握：中；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**格子**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| score_weights | A | 0 | 1 |
| recommendation_wording | A | 0 | 1 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-012_marketo__operational_health_simple.md](../../records/022_packages/022_impl-012_marketo__operational_health_simple.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-012_marketo__operational_health_simple/022_impl-012_marketo__operational_health_simple.json`。
- 比较结果：[022_reruns_impl-012_marketo__operational_health_simple.json](../022_reruns_impl-012_marketo__operational_health_simple.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-012/docs/data_contract.yaml`。

原件第1580–1699行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/sql/marts/marketo__operational_health_simple.sql`；原件第1–1行。

```sql
   1: WITH daily AS (SELECT CAST(activity_timestamp AS DATE) AS activity_date,COUNT(*) AS daily_emails_sent,COUNT(DISTINCT lead_id) AS unique_recipients,COUNT(DISTINCT campaign_id) AS active_campaigns,COUNT(DISTINCT email_template_id) AS unique_templates,COUNT(*) FILTER(WHERE was_delivered) AS delivered,COUNT(*) FILTER(WHERE was_opened) AS opened,COUNT(*) FILTER(WHERE was_clicked) AS clicked,COUNT(*) FILTER(WHERE was_bounced) AS bounced,COUNT(*) FILTER(WHERE was_unsubscribed) AS unsubscribes,ROUND(COUNT(*) FILTER(WHERE was_delivered)::DOUBLE/COUNT(*)*100,2) AS daily_delivery_rate_pct,ROUND(CASE WHEN COUNT(*) FILTER(WHERE was_delivered)=0 THEN 0 ELSE COUNT(*) FILTER(WHERE was_opened)::DOUBLE/COUNT(*) FILTER(WHERE was_delivered)*100 END,2) AS daily_open_rate_pct,ROUND(COUNT(*) FILTER(WHERE was_bounced)::DOUBLE/COUNT(*)*100,2) AS daily_bounce_rate_pct FROM marts.marketo__email_sends WHERE activity_timestamp IS NOT NULL GROUP BY 1), daily_summary AS (SELECT CASE WHEN AVG(daily_emails_sent)>=1000 THEN 'High Volume System' WHEN AVG(daily_emails_sent)>=500 THEN 'Medium Volume System' WHEN AVG(daily_emails_sent)>=100 THEN 'Low Volume System' ELSE 'Minimal Volume System' END AS system_volume_classification,CASE WHEN STDDEV_SAMP(daily_delivery_rate_pct)<=5 THEN 'Stable' WHEN STDDEV_SAMP(daily_delivery_rate_pct)<=10 THEN 'Moderate Variance' ELSE 'High Variance' END AS delivery_stability,COUNT(*)::BIGINT AS days_of_data,MIN(activity_date) AS earliest_activity_date,MAX(activity_date) AS latest_activity_date,STDDEV_SAMP(daily_delivery_rate_pct) AS delivery_rate_volatility,STDDEV_SAMP(daily_open_rate_pct) AS open_rate_volatility,STDDEV_SAMP(daily_bounce_rate_pct) AS bounce_rate_volatility,AVG(daily_emails_sent) FILTER(WHERE activity_date>=CURRENT_DATE-INTERVAL 6 DAY) AS avg_daily_volume_last_7_days,AVG(daily_delivery_rate_pct) FILTER(WHERE activity_date>=CURRENT_DATE-INTERVAL 6 DAY) AS avg_delivery_rate_last_7_days,AVG(daily_open_rate_pct) FILTER(WHERE activity_date>=CURRENT_DATE-INTERVAL 6 DAY) AS avg_open_rate_last_7_days FROM daily), deliverability AS (SELECT COUNT(*)::BIGINT AS total_email_attempts,COUNT(*) FILTER(WHERE was_delivered)::BIGINT AS successful_deliveries,COUNT(*) FILTER(WHERE was_bounced)::BIGINT AS total_bounces,ROUND(COUNT(*) FILTER(WHERE was_delivered)::DOUBLE/NULLIF(COUNT(*),0)*100,2) AS overall_delivery_rate_pct,ROUND(COUNT(*) FILTER(WHERE was_bounced)::DOUBLE/NULLIF(COUNT(*),0)*100,2) AS overall_bounce_rate_pct,ROUND(COUNT(*) FILTER(WHERE was_delivered AND activity_timestamp>=CURRENT_TIMESTAMP-INTERVAL 30 DAY)::DOUBLE/NULLIF(COUNT(*) FILTER(WHERE activity_timestamp>=CURRENT_TIMESTAMP-INTERVAL 30 DAY),0)*100,2) AS recent_delivery_rate_pct FROM marts.marketo__email_sends), campaign_summary AS (SELECT COUNT(*)::BIGINT AS total_campaigns,COUNT(*) FILTER(WHERE open_rate>=25)::BIGINT AS healthy_campaigns,COUNT(*) FILTER(WHERE open_rate<5)::BIGINT AS critical_campaigns,COUNT(*) FILTER(WHERE bounce_rate>10)::BIGINT AS campaigns_with_bounce_issues FROM (SELECT campaign_id,AVG(CASE WHEN was_opened THEN 100.0 ELSE 0.0 END) AS open_rate,AVG(CASE WHEN was_bounced THEN 100.0 ELSE 0.0 END) AS bounce_rate FROM marts.marketo__email_sends WHERE campaign_id IS NOT NULL GROUP BY campaign_id) c), lead_rows AS (SELECT l.lead_id,es.activity_id,es.was_clicked,es.was_opened,es.was_delivered,es.count_opens,es.count_clicks FROM intermediate.int_marketo__lead l LEFT JOIN marts.marketo__email_sends es USING(lead_id) WHERE NOT l.is_deleted AND NOT l.is_merged), lead_summary AS (SELECT COUNT(*)::BIGINT AS total_leads,COUNT(*) FILTER(WHERE activity_id IS NOT NULL AND was_clicked)::BIGINT AS engaged_leads,COUNT(*) FILTER(WHERE activity_id IS NOT NULL AND was_opened AND NOT was_clicked)::BIGINT AS moderately_engaged_leads,COUNT(*) FILTER(WHERE activity_id IS NOT NULL AND NOT was_opened)::BIGINT AS low_engaged_leads,COUNT(*) FILTER(WHERE activity_id IS NULL)::BIGINT AS inactive_leads,ROUND(COUNT(*) FILTER(WHERE activity_id IS NOT NULL AND was_clicked)::DOUBLE/NULLIF(COUNT(*),0)*100,2) AS engaged_leads_pct,ROUND(COUNT(*) FILTER(WHERE activity_id IS NULL OR NOT was_delivered)::DOUBLE/NULLIF(COUNT(*),0)*100,2) AS at_risk_leads_pct,ROUND(AVG(CASE WHEN activity_id IS NULL THEN 0 ELSE COALESCE(count_opens,0)*5+COALESCE(count_clicks,0)*10 END),2) AS avg_lead_score FROM lead_rows), combined AS (SELECT CURRENT_DATE AS health_check_date,CURRENT_TIMESTAMP AS health_check_timestamp,d.*,COALESCE(x.total_email_attempts,0) AS total_email_attempts,COALESCE(x.successful_deliveries,0) AS successful_deliveries,COALESCE(x.total_bounces,0) AS total_bounces,COALESCE(x.overall_delivery_rate_pct,0) AS overall_delivery_rate_pct,COALESCE(x.overall_bounce_rate_pct,0) AS overall_bounce_rate_pct,COALESCE(x.recent_delivery_rate_pct,0) AS recent_delivery_rate_pct,l.*,c.*,ROUND(CASE WHEN c.total_campaigns=0 THEN 0 ELSE c.healthy_campaigns::DOUBLE/c.total_campaigns*100 END,2) AS healthy_campaigns_pct FROM daily_summary d CROSS JOIN deliverability x CROSS JOIN campaign_summary c CROSS JOIN lead_summary l) SELECT health_check_date,health_check_timestamp,system_volume_classification,delivery_stability,days_of_data,earliest_activity_date,latest_activity_date,total_email_attempts,successful_deliveries,total_bounces,overall_delivery_rate_pct,overall_bounce_rate_pct,recent_delivery_rate_pct,CASE WHEN overall_delivery_rate_pct>=95 THEN 'Excellent' WHEN overall_delivery_rate_pct>=90 THEN 'Good' WHEN overall_delivery_rate_pct>=85 THEN 'Fair' WHEN overall_delivery_rate_pct>=80 THEN 'Poor' ELSE 'Critical' END AS deliverability_health_status,total_leads,engaged_leads,moderately_engaged_leads,low_engaged_leads,inactive_leads,COALESCE(engaged_leads_pct,0) AS engaged_leads_pct,COALESCE(at_risk_leads_pct,0) AS at_risk_leads_pct,COALESCE(avg_lead_score,0) AS avg_lead_score,CASE WHEN engaged_leads_pct>=40 AND at_risk_leads_pct<=20 THEN 'Excellent' WHEN engaged_leads_pct>=25 AND at_risk_leads_pct<=30 THEN 'Good' WHEN engaged_leads_pct>=15 AND at_risk_leads_pct<=40 THEN 'Fair' WHEN engaged_leads_pct>=5 THEN 'Poor' ELSE 'Critical' END AS lead_database_health_status,total_campaigns,healthy_campaigns,critical_campaigns,campaigns_with_bounce_issues,healthy_campaigns_pct,avg_daily_volume_last_7_days,avg_delivery_rate_last_7_days,avg_open_rate_last_7_days,ROUND(delivery_rate_volatility,2) AS delivery_rate_volatility,ROUND(open_rate_volatility,2) AS open_rate_volatility,ROUND(bounce_rate_volatility,2) AS bounce_rate_volatility,CAST(ROUND((CASE WHEN overall_delivery_rate_pct>=95 THEN 25 WHEN overall_delivery_rate_pct>=90 THEN 20 WHEN overall_delivery_rate_pct>=85 THEN 15 ELSE 5 END)+(CASE WHEN engaged_leads_pct>=40 THEN 25 WHEN engaged_leads_pct>=25 THEN 20 WHEN engaged_leads_pct>=15 THEN 15 ELSE 5 END)+(CASE WHEN healthy_campaigns_pct>=50 THEN 25 WHEN healthy_campaigns_pct>=25 THEN 20 WHEN healthy_campaigns_pct>=10 THEN 15 ELSE 5 END)+(CASE WHEN delivery_stability='Stable' THEN 25 WHEN delivery_stability='Moderate Variance' THEN 15 ELSE 5 END)) AS INTEGER) AS overall_health_score,CASE WHEN overall_delivery_rate_pct<85 THEN 'Focus on improving email deliverability' WHEN at_risk_leads_pct>30 THEN 'Launch re-engagement campaigns for at-risk leads' WHEN critical_campaigns>3 THEN 'Optimize underperforming campaigns' WHEN delivery_stability='High Variance' THEN 'Stabilize email sending patterns' ELSE 'Continue current efforts' END AS primary_recommendation FROM combined
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-012/sql/marts/marketo__operational_health_simple.sql`；原件第1–265行。

```sql
   1: -- Marts: Simplified marketing operations health monitoring dashboard
   2: 
   3: WITH daily_email_volume AS (
   4:     SELECT 
   5:         DATE(activity_timestamp) as activity_date,
   6:         COUNT(*) as daily_emails_sent,
   7:         COUNT(DISTINCT lead_id) as daily_unique_recipients,
   8:         COUNT(DISTINCT campaign_id) as daily_active_campaigns,
   9:         COUNT(DISTINCT email_template_id) as daily_unique_templates,
  10:         
  11:         -- Daily engagement metrics
  12:         COUNT(CASE WHEN was_delivered THEN 1 END) as daily_emails_delivered,
  13:         COUNT(CASE WHEN was_opened THEN 1 END) as daily_emails_opened,
  14:         COUNT(CASE WHEN was_clicked THEN 1 END) as daily_emails_clicked,
  15:         COUNT(CASE WHEN was_bounced THEN 1 END) as daily_emails_bounced,
  16:         COUNT(CASE WHEN was_unsubscribed THEN 1 END) as daily_unsubscribes,
  17:         
  18:         -- Daily quality metrics
  19:         CASE 
  20:             WHEN COUNT(*) > 0 
  21:             THEN ROUND((COUNT(CASE WHEN was_delivered THEN 1 END)::DOUBLE / COUNT(*)) * 100, 2)
  22:             ELSE 0 
  23:         END as daily_delivery_rate_pct,
  24:         
  25:         CASE 
  26:             WHEN COUNT(CASE WHEN was_delivered THEN 1 END) > 0 
  27:             THEN ROUND((COUNT(CASE WHEN was_opened THEN 1 END)::DOUBLE / COUNT(CASE WHEN was_delivered THEN 1 END)) * 100, 2)
  28:             ELSE 0 
  29:         END as daily_open_rate_pct,
  30:         
  31:         CASE 
  32:             WHEN COUNT(*) > 0 
  33:             THEN ROUND((COUNT(CASE WHEN was_bounced THEN 1 END)::DOUBLE / COUNT(*)) * 100, 2)
  34:             ELSE 0 
  35:         END as daily_bounce_rate_pct
  36:         
  37:     FROM marts.marketo__email_sends
  38:     WHERE activity_timestamp IS NOT NULL
  39:     GROUP BY DATE(activity_timestamp)
  40: ),
  41: 
  42: -- Lead database health (simplified)
  43: lead_database_health AS (
  44:     SELECT 
  45:         COUNT(*) as total_leads,
  46:         
  47:         -- Simple engagement classification based on email activity
  48:         COUNT(CASE WHEN es.lead_id IS NOT NULL AND es.was_clicked THEN 1 END) as engaged_leads,
  49:         COUNT(CASE WHEN es.lead_id IS NOT NULL AND es.was_opened AND NOT es.was_clicked THEN 1 END) as moderately_engaged_leads,
  50:         COUNT(CASE WHEN es.lead_id IS NOT NULL AND NOT es.was_opened THEN 1 END) as low_engaged_leads,
  51:         COUNT(CASE WHEN es.lead_id IS NULL THEN 1 END) as inactive_leads,
  52:         
  53:         -- Lead health percentages
  54:         ROUND((COUNT(CASE WHEN es.lead_id IS NOT NULL AND es.was_clicked THEN 1 END)::DOUBLE / COUNT(*)) * 100, 2) as engaged_leads_pct,
  55:         ROUND((COUNT(CASE WHEN es.lead_id IS NULL OR NOT es.was_delivered THEN 1 END)::DOUBLE / COUNT(*)) * 100, 2) as at_risk_leads_pct,
  56:         
  57:         -- Average metrics
  58:         AVG(CASE WHEN es.lead_id IS NOT NULL THEN es.count_opens * 5 + es.count_clicks * 10 ELSE 0 END) as avg_lead_score
  59:         
  60:     FROM intermediate.int_marketo__lead l
  61:     LEFT JOIN marts.marketo__email_sends es ON l.lead_id = es.lead_id
  62:     WHERE NOT l.is_deleted AND NOT l.is_merged
  63: ),
  64: 
  65: -- Email deliverability health
  66: deliverability_health AS (
  67:     SELECT 
  68:         -- Overall deliverability metrics
  69:         COUNT(*) as total_email_attempts,
  70:         COUNT(CASE WHEN was_delivered THEN 1 END) as successful_deliveries,
  71:         COUNT(CASE WHEN was_bounced THEN 1 END) as total_bounces,
  72:         
  73:         -- Deliverability rates
  74:         ROUND((COUNT(CASE WHEN was_delivered THEN 1 END)::DOUBLE / COUNT(*)) * 100, 2) as overall_delivery_rate_pct,
  75:         ROUND((COUNT(CASE WHEN was_bounced THEN 1 END)::DOUBLE / COUNT(*)) * 100, 2) as overall_bounce_rate_pct,
  76:         
  77:         -- Recent deliverability (last 30 days)
  78:         COUNT(CASE WHEN was_delivered AND activity_timestamp >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END) as recent_deliveries,
  79:         COUNT(CASE WHEN was_bounced AND activity_timestamp >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END) as recent_bounces,
  80:         
  81:         CASE 
  82:             WHEN COUNT(CASE WHEN activity_timestamp >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END) > 0
  83:             THEN ROUND((COUNT(CASE WHEN was_delivered AND activity_timestamp >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END)::DOUBLE / 
  84:                        COUNT(CASE WHEN activity_timestamp >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END)) * 100, 2)
  85:             ELSE 0
  86:         END as recent_delivery_rate_pct
  87:         
  88:     FROM marts.marketo__email_sends
  89: ),
  90: 
  91: -- Campaign health
  92: campaign_health AS (
  93:     SELECT 
  94:         COUNT(DISTINCT campaign_id) as total_campaigns,
  95:         COUNT(DISTINCT CASE WHEN avg_open_rate >= 25 THEN campaign_id END) as healthy_campaigns,
  96:         COUNT(DISTINCT CASE WHEN avg_open_rate < 5 THEN campaign_id END) as critical_campaigns,
  97:         COUNT(DISTINCT CASE WHEN avg_bounce_rate > 10 THEN campaign_id END) as campaigns_with_bounce_issues
  98:     FROM (
  99:         SELECT 
 100:             campaign_id,
 101:             AVG(CASE WHEN was_opened THEN 1.0 ELSE 0.0 END) * 100 as avg_open_rate,
 102:             AVG(CASE WHEN was_bounced THEN 1.0 ELSE 0.0 END) * 100 as avg_bounce_rate
 103:         FROM marts.marketo__email_sends
 104:         WHERE campaign_id IS NOT NULL
 105:         GROUP BY campaign_id
 106:     ) camp_stats
 107: ),
 108: 
 109: -- System health indicators
 110: system_health_indicators AS (
 111:     SELECT 
 112:         -- Volume health indicators
 113:         CASE 
 114:             WHEN AVG(daily_emails_sent) >= 1000 THEN 'High Volume System'
 115:             WHEN AVG(daily_emails_sent) >= 500 THEN 'Medium Volume System'
 116:             WHEN AVG(daily_emails_sent) >= 100 THEN 'Low Volume System'
 117:             ELSE 'Minimal Volume System'
 118:         END as system_volume_classification,
 119:         
 120:         -- Performance consistency indicators
 121:         STDDEV(daily_delivery_rate_pct) as delivery_rate_volatility,
 122:         STDDEV(daily_open_rate_pct) as open_rate_volatility,
 123:         STDDEV(daily_bounce_rate_pct) as bounce_rate_volatility,
 124:         
 125:         -- System stability indicators
 126:         CASE 
 127:             WHEN STDDEV(daily_delivery_rate_pct) <= 5 THEN 'Stable'
 128:             WHEN STDDEV(daily_delivery_rate_pct) <= 10 THEN 'Moderate Variance'
 129:             ELSE 'High Variance'
 130:         END as delivery_stability,
 131:         
 132:         COUNT(*) as days_of_data,
 133:         MIN(activity_date) as earliest_activity_date,
 134:         MAX(activity_date) as latest_activity_date
 135:         
 136:     FROM daily_email_volume
 137: ),
 138: 
 139: final AS (
 140:     SELECT 
 141:         CURRENT_DATE as health_check_date,
 142:         CURRENT_TIMESTAMP as health_check_timestamp,
 143:         
 144:         -- System overview
 145:         shi.system_volume_classification,
 146:         shi.delivery_stability,
 147:         shi.days_of_data,
 148:         shi.earliest_activity_date,
 149:         shi.latest_activity_date,
 150:         
 151:         -- Deliverability health
 152:         dh.total_email_attempts,
 153:         dh.successful_deliveries,
 154:         dh.total_bounces,
 155:         dh.overall_delivery_rate_pct,
 156:         dh.overall_bounce_rate_pct,
 157:         dh.recent_delivery_rate_pct,
 158:         
 159:         -- Overall deliverability health status
 160:         CASE 
 161:             WHEN dh.overall_delivery_rate_pct >= 95 THEN 'Excellent'
 162:             WHEN dh.overall_delivery_rate_pct >= 90 THEN 'Good'
 163:             WHEN dh.overall_delivery_rate_pct >= 85 THEN 'Fair'
 164:             WHEN dh.overall_delivery_rate_pct >= 80 THEN 'Poor'
 165:             ELSE 'Critical'
 166:         END as deliverability_health_status,
 167:         
 168:         -- Lead database health
 169:         ldh.total_leads,
 170:         ldh.engaged_leads,
 171:         ldh.moderately_engaged_leads,
 172:         ldh.low_engaged_leads,
 173:         ldh.inactive_leads,
 174:         ldh.engaged_leads_pct,
 175:         ldh.at_risk_leads_pct,
 176:         ROUND(ldh.avg_lead_score, 2) as avg_lead_score,
 177:         
 178:         -- Lead database health status
 179:         CASE 
 180:             WHEN ldh.engaged_leads_pct >= 40 AND ldh.at_risk_leads_pct <= 20 THEN 'Excellent'
 181:             WHEN ldh.engaged_leads_pct >= 25 AND ldh.at_risk_leads_pct <= 30 THEN 'Good'
 182:             WHEN ldh.engaged_leads_pct >= 15 AND ldh.at_risk_leads_pct <= 40 THEN 'Fair'
 183:             WHEN ldh.engaged_leads_pct >= 5 THEN 'Poor'
 184:             ELSE 'Critical'
 185:         END as lead_database_health_status,
 186:         
 187:         -- Campaign health summary
 188:         ch.total_campaigns,
 189:         ch.healthy_campaigns,
 190:         ch.critical_campaigns,
 191:         ch.campaigns_with_bounce_issues,
 192:         
 193:         -- Campaign health percentage
 194:         CASE 
 195:             WHEN ch.total_campaigns > 0
 196:             THEN ROUND((ch.healthy_campaigns::DOUBLE / ch.total_campaigns) * 100, 2)
 197:             ELSE 0
 198:         END as healthy_campaigns_pct,
 199:         
 200:         -- Recent activity trends (last 7 days)
 201:         AVG(CASE WHEN dev.activity_date >= CURRENT_DATE - INTERVAL '7 days' THEN dev.daily_emails_sent END) as avg_daily_volume_last_7_days,
 202:         AVG(CASE WHEN dev.activity_date >= CURRENT_DATE - INTERVAL '7 days' THEN dev.daily_delivery_rate_pct END) as avg_delivery_rate_last_7_days,
 203:         AVG(CASE WHEN dev.activity_date >= CURRENT_DATE - INTERVAL '7 days' THEN dev.daily_open_rate_pct END) as avg_open_rate_last_7_days,
 204:         
 205:         -- Performance volatility indicators
 206:         ROUND(shi.delivery_rate_volatility, 2) as delivery_rate_volatility,
 207:         ROUND(shi.open_rate_volatility, 2) as open_rate_volatility,
 208:         ROUND(shi.bounce_rate_volatility, 2) as bounce_rate_volatility,
 209:         
 210:         -- Overall health score (weighted composite)
 211:         ROUND(
 212:             (CASE 
 213:                 WHEN dh.overall_delivery_rate_pct >= 95 THEN 30
 214:                 WHEN dh.overall_delivery_rate_pct >= 90 THEN 25
 215:                 WHEN dh.overall_delivery_rate_pct >= 85 THEN 20
 216:                 WHEN dh.overall_delivery_rate_pct >= 80 THEN 15
 217:                 ELSE 10
 218:             END) +
 219:             (CASE 
 220:                 WHEN ldh.engaged_leads_pct >= 40 THEN 30
 221:                 WHEN ldh.engaged_leads_pct >= 25 THEN 25
 222:                 WHEN ldh.engaged_leads_pct >= 15 THEN 20
 223:                 WHEN ldh.engaged_leads_pct >= 5 THEN 15
 224:                 ELSE 10
 225:             END) +
 226:             (CASE 
 227:                 WHEN ch.total_campaigns > 0 AND (ch.healthy_campaigns::DOUBLE / ch.total_campaigns) >= 0.8 THEN 25
 228:                 WHEN ch.total_campaigns > 0 AND (ch.healthy_campaigns::DOUBLE / ch.total_campaigns) >= 0.6 THEN 20
 229:                 WHEN ch.total_campaigns > 0 AND (ch.healthy_campaigns::DOUBLE / ch.total_campaigns) >= 0.4 THEN 15
 230:                 ELSE 10
 231:             END) +
 232:             (CASE 
 233:                 WHEN shi.delivery_stability = 'Stable' THEN 15
 234:                 WHEN shi.delivery_stability = 'Moderate Variance' THEN 10
 235:                 ELSE 5
 236:             END), 2
 237:         ) as overall_health_score,
 238:         
 239:         -- Health recommendations
 240:         CASE 
 241:             WHEN dh.overall_delivery_rate_pct < 85 THEN 'Focus on deliverability improvement'
 242:             WHEN ldh.at_risk_leads_pct > 30 THEN 'Implement lead re-engagement campaigns'
 243:             WHEN ch.critical_campaigns > 3 THEN 'Optimize underperforming campaigns'
 244:             WHEN shi.delivery_stability = 'High Variance' THEN 'Stabilize sending patterns'
 245:             ELSE 'Continue current optimization efforts'
 246:         END as primary_recommendation
 247:         
 248:     FROM system_health_indicators shi
 249:     CROSS JOIN deliverability_health dh
 250:     CROSS JOIN lead_database_health ldh
 251:     CROSS JOIN campaign_health ch
 252:     LEFT JOIN daily_email_volume dev ON 1=1
 253:     GROUP BY 
 254:         shi.system_volume_classification, shi.delivery_stability, shi.days_of_data,
 255:         shi.earliest_activity_date, shi.latest_activity_date, shi.delivery_rate_volatility, 
 256:         shi.open_rate_volatility, shi.bounce_rate_volatility,
 257:         dh.total_email_attempts, dh.successful_deliveries, dh.total_bounces, dh.overall_delivery_rate_pct,
 258:         dh.overall_bounce_rate_pct, dh.recent_delivery_rate_pct,
 259:         ldh.total_leads, ldh.engaged_leads, ldh.moderately_engaged_leads, ldh.low_engaged_leads, 
 260:         ldh.inactive_leads, ldh.engaged_leads_pct, ldh.at_risk_leads_pct, ldh.avg_lead_score,
 261:         ch.total_campaigns, ch.healthy_campaigns, ch.critical_campaigns, ch.campaigns_with_bounce_issues
 262: )
 263: 
 264: SELECT *
 265: FROM final
```

## 3. agent看到的材料与不确定性

已检视该题全部57个原始归档事件（原输出显式截断事件：[]），最终报告与写报告动作。程序读取YAML不等于把完整YAML显示给agent；不推断未留存思考。


四档：**没有迹象**。

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

### 诊断（允许gold，不计5条）

`records/022_diagnostics.json` 本表条目：

```json
{"index": 3, "kind": "诊断查询", "queries": [{"label": "实际分歧", "sql": "SELECT overall_health_score,primary_recommendation FROM gold.marts.marketo__operational_health_simple", "columns": ["overall_health_score", "primary_recommendation"], "result": [[45, "Focus on deliverability improvement"]]}]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-012/marketo.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 22:47:14.925+08'", "count": 3}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 4}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["health_check_date", "health_check_timestamp"]`；比较列：`["at_risk_leads_pct", "avg_lead_score", "avg_open_rate_last_7_days", "bounce_rate_volatility", "campaigns_with_bounce_issues", "critical_campaigns", "days_of_data", "deliverability_health_status", "delivery_rate_volatility", "delivery_stability", "earliest_activity_date", "engaged_leads", "engaged_leads_pct", "health_check_date", "health_check_timestamp", "healthy_campaigns", "healthy_campaigns_pct", "inactive_leads", "latest_activity_date", "lead_database_health_status", "low_engaged_leads", "moderately_engaged_leads", "overall_bounce_rate_pct", "overall_delivery_rate_pct", "overall_health_score", "primary_recommendation", "recent_delivery_rate_pct", "successful_deliveries", "system_volume_classification", "total_bounces", "total_campaigns", "total_email_attempts", "total_leads"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 1/1 | 1/1 | 0/0 | 0 | 2 | 66 | False |
| L1 | 1/1 | 1/1 | 0/0 | 0 | 2 | 66 | False |
| L2 | 1/1 | 1/1 | 0/0 | 0 | 2 | 66 | False |
| L3 | 1/1 | 1/1 | 0/0 | 0 | 2 | 66 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| health_check_date | 0 | 0 | 0 | 0 |
| health_check_timestamp | 0 | 0 | 0 | 0 |
| at_risk_leads_pct | 0 | 0 | 0 | 0 |
| avg_lead_score | 0 | 0 | 0 | 0 |
| avg_open_rate_last_7_days | 0 | 0 | 0 | 0 |
| bounce_rate_volatility | 0 | 0 | 0 | 0 |
| campaigns_with_bounce_issues | 0 | 0 | 0 | 0 |
| critical_campaigns | 0 | 0 | 0 | 0 |
| days_of_data | 0 | 0 | 0 | 0 |
| deliverability_health_status | 0 | 0 | 0 | 0 |
| delivery_rate_volatility | 0 | 0 | 0 | 0 |
| delivery_stability | 0 | 0 | 0 | 0 |
| earliest_activity_date | 0 | 0 | 0 | 0 |
| engaged_leads | 0 | 0 | 0 | 0 |
| engaged_leads_pct | 0 | 0 | 0 | 0 |
| healthy_campaigns | 0 | 0 | 0 | 0 |
| healthy_campaigns_pct | 0 | 0 | 0 | 0 |
| inactive_leads | 0 | 0 | 0 | 0 |
| latest_activity_date | 0 | 0 | 0 | 0 |
| lead_database_health_status | 0 | 0 | 0 | 0 |
| low_engaged_leads | 0 | 0 | 0 | 0 |
| moderately_engaged_leads | 0 | 0 | 0 | 0 |
| overall_bounce_rate_pct | 0 | 0 | 0 | 0 |
| overall_delivery_rate_pct | 0 | 0 | 0 | 0 |
| overall_health_score | 0 | 0 | 0 | 0 |
| primary_recommendation | 0 | 0 | 0 | 0 |
| recent_delivery_rate_pct | 0 | 0 | 0 | 0 |
| successful_deliveries | 0 | 0 | 0 | 0 |
| system_volume_classification | 0 | 0 | 0 | 0 |
| total_bounces | 0 | 0 | 0 | 0 |
| total_campaigns | 0 | 0 | 0 | 0 |
| total_email_attempts | 0 | 0 | 0 | 0 |
| total_leads | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-012_marketo__operational_health_simple/baseline.sql`；SHA-256：`74ab1c8a12dbeb2b5409e616cd9f9bb8c5429738aebc3acf774630ed5dd22e70`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 1/1 | 0/0 | 0/0 | 1 | 1 | 2 | False |
| L1 | 1/1 | 0/0 | 0/0 | 1 | 1 | 2 | False |
| L2 | 1/1 | 0/0 | 0/0 | 1 | 1 | 2 | False |
| L3 | 1/1 | 0/0 | 0/0 | 1 | 1 | 2 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| health_check_date | 0 | 0 | 0 | 0 |
| health_check_timestamp | 0 | 0 | 0 | 0 |
| at_risk_leads_pct | 0 | 0 | 0 | 0 |
| avg_lead_score | 0 | 0 | 0 | 0 |
| avg_open_rate_last_7_days | 0 | 0 | 0 | 0 |
| bounce_rate_volatility | 0 | 0 | 0 | 0 |
| campaigns_with_bounce_issues | 0 | 0 | 0 | 0 |
| critical_campaigns | 0 | 0 | 0 | 0 |
| days_of_data | 0 | 0 | 0 | 0 |
| deliverability_health_status | 0 | 0 | 0 | 0 |
| delivery_rate_volatility | 0 | 0 | 0 | 0 |
| delivery_stability | 0 | 0 | 0 | 0 |
| earliest_activity_date | 0 | 0 | 0 | 0 |
| engaged_leads | 0 | 0 | 0 | 0 |
| engaged_leads_pct | 0 | 0 | 0 | 0 |
| healthy_campaigns | 0 | 0 | 0 | 0 |
| healthy_campaigns_pct | 0 | 0 | 0 | 0 |
| inactive_leads | 0 | 0 | 0 | 0 |
| latest_activity_date | 0 | 0 | 0 | 0 |
| lead_database_health_status | 0 | 0 | 0 | 0 |
| low_engaged_leads | 0 | 0 | 0 | 0 |
| moderately_engaged_leads | 0 | 0 | 0 | 0 |
| overall_bounce_rate_pct | 0 | 0 | 0 | 0 |
| overall_delivery_rate_pct | 0 | 0 | 0 | 0 |
| overall_health_score | 1 | 1 | 1 | 1 |
| primary_recommendation | 1 | 1 | 1 | 1 |
| recent_delivery_rate_pct | 0 | 0 | 0 | 0 |
| successful_deliveries | 0 | 0 | 0 | 0 |
| system_volume_classification | 0 | 0 | 0 | 0 |
| total_bounces | 0 | 0 | 0 | 0 |
| total_campaigns | 0 | 0 | 0 | 0 |
| total_email_attempts | 0 | 0 | 0 | 0 |
| total_leads | 0 | 0 | 0 | 0 |

### score_weights

SQL：`data/022_work/impl-012_marketo__operational_health_simple/score_weights.sql`；SHA-256：`b9a9527a0639871f5f5eec01d6d32dd3a17affd490b30da8881dc377ae19adaa`。

替换offset=6546，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CAST(ROUND((CASE WHEN overall_delivery_rate_pct>=95 THEN 25 WHEN overall_delivery_rate_pct>=90 THEN 20 WHEN overall_delivery_rate_pct>=85 THEN 15 ELSE 5 END)+(CASE WHEN engaged_leads_pct>=40 THEN 25 WHEN engaged_leads_pct>=25 THEN 20 WHEN engaged_leads_pct>=15 THEN 15 ELSE 5 END)+(CASE WHEN healthy_campaigns_pct>=50 THEN 25 WHEN healthy_campaigns_pct>=25 THEN 20 WHEN healthy_campaigns_pct>=10 THEN 15 ELSE 5 END)+(CASE WHEN delivery_stability='Stable' THEN 25 WHEN delivery_stability='Moderate Variance' THEN 15 ELSE 5 END)) AS INTEGER) AS overall_health_score
-- 新
CAST(ROUND((CASE WHEN overall_delivery_rate_pct>=95 THEN 30 WHEN overall_delivery_rate_pct>=90 THEN 25 WHEN overall_delivery_rate_pct>=85 THEN 20 WHEN overall_delivery_rate_pct>=80 THEN 15 ELSE 10 END)+(CASE WHEN engaged_leads_pct>=40 THEN 30 WHEN engaged_leads_pct>=25 THEN 25 WHEN engaged_leads_pct>=15 THEN 20 WHEN engaged_leads_pct>=5 THEN 15 ELSE 10 END)+(CASE WHEN healthy_campaigns_pct>=80 THEN 25 WHEN healthy_campaigns_pct>=60 THEN 20 WHEN healthy_campaigns_pct>=40 THEN 15 ELSE 10 END)+(CASE WHEN delivery_stability='Stable' THEN 15 WHEN delivery_stability='Moderate Variance' THEN 10 ELSE 5 END),2) AS INTEGER) AS overall_health_score
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 1/1 | 0/0 | 0/0 | 1 | 1 | 1 | False |
| L1 | 1/1 | 0/0 | 0/0 | 1 | 1 | 1 | False |
| L2 | 1/1 | 0/0 | 0/0 | 1 | 1 | 1 | False |
| L3 | 1/1 | 0/0 | 0/0 | 1 | 1 | 1 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| health_check_date | 0 | 0 | 0 | 0 |
| health_check_timestamp | 0 | 0 | 0 | 0 |
| at_risk_leads_pct | 0 | 0 | 0 | 0 |
| avg_lead_score | 0 | 0 | 0 | 0 |
| avg_open_rate_last_7_days | 0 | 0 | 0 | 0 |
| bounce_rate_volatility | 0 | 0 | 0 | 0 |
| campaigns_with_bounce_issues | 0 | 0 | 0 | 0 |
| critical_campaigns | 0 | 0 | 0 | 0 |
| days_of_data | 0 | 0 | 0 | 0 |
| deliverability_health_status | 0 | 0 | 0 | 0 |
| delivery_rate_volatility | 0 | 0 | 0 | 0 |
| delivery_stability | 0 | 0 | 0 | 0 |
| earliest_activity_date | 0 | 0 | 0 | 0 |
| engaged_leads | 0 | 0 | 0 | 0 |
| engaged_leads_pct | 0 | 0 | 0 | 0 |
| healthy_campaigns | 0 | 0 | 0 | 0 |
| healthy_campaigns_pct | 0 | 0 | 0 | 0 |
| inactive_leads | 0 | 0 | 0 | 0 |
| latest_activity_date | 0 | 0 | 0 | 0 |
| lead_database_health_status | 0 | 0 | 0 | 0 |
| low_engaged_leads | 0 | 0 | 0 | 0 |
| moderately_engaged_leads | 0 | 0 | 0 | 0 |
| overall_bounce_rate_pct | 0 | 0 | 0 | 0 |
| overall_delivery_rate_pct | 0 | 0 | 0 | 0 |
| overall_health_score | 0 | 0 | 0 | 0 |
| primary_recommendation | 1 | 1 | 1 | 1 |
| recent_delivery_rate_pct | 0 | 0 | 0 | 0 |
| successful_deliveries | 0 | 0 | 0 | 0 |
| system_volume_classification | 0 | 0 | 0 | 0 |
| total_bounces | 0 | 0 | 0 | 0 |
| total_campaigns | 0 | 0 | 0 | 0 |
| total_email_attempts | 0 | 0 | 0 | 0 |
| total_leads | 0 | 0 | 0 | 0 |

### recommendation_wording

SQL：`data/022_work/impl-012_marketo__operational_health_simple/recommendation_wording.sql`；SHA-256：`233a9caeee11e70ca2815ecd7e581d6d09f2813146695049e7fa13d2d568e40e`。

替换offset=7154，原表达式所在行约1（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
'Focus on improving email deliverability'
-- 新
'Focus on deliverability improvement'
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 1/1 | 0/0 | 0/0 | 1 | 1 | 1 | False |
| L1 | 1/1 | 0/0 | 0/0 | 1 | 1 | 1 | False |
| L2 | 1/1 | 0/0 | 0/0 | 1 | 1 | 1 | False |
| L3 | 1/1 | 0/0 | 0/0 | 1 | 1 | 1 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| health_check_date | 0 | 0 | 0 | 0 |
| health_check_timestamp | 0 | 0 | 0 | 0 |
| at_risk_leads_pct | 0 | 0 | 0 | 0 |
| avg_lead_score | 0 | 0 | 0 | 0 |
| avg_open_rate_last_7_days | 0 | 0 | 0 | 0 |
| bounce_rate_volatility | 0 | 0 | 0 | 0 |
| campaigns_with_bounce_issues | 0 | 0 | 0 | 0 |
| critical_campaigns | 0 | 0 | 0 | 0 |
| days_of_data | 0 | 0 | 0 | 0 |
| deliverability_health_status | 0 | 0 | 0 | 0 |
| delivery_rate_volatility | 0 | 0 | 0 | 0 |
| delivery_stability | 0 | 0 | 0 | 0 |
| earliest_activity_date | 0 | 0 | 0 | 0 |
| engaged_leads | 0 | 0 | 0 | 0 |
| engaged_leads_pct | 0 | 0 | 0 | 0 |
| healthy_campaigns | 0 | 0 | 0 | 0 |
| healthy_campaigns_pct | 0 | 0 | 0 | 0 |
| inactive_leads | 0 | 0 | 0 | 0 |
| latest_activity_date | 0 | 0 | 0 | 0 |
| lead_database_health_status | 0 | 0 | 0 | 0 |
| low_engaged_leads | 0 | 0 | 0 | 0 |
| moderately_engaged_leads | 0 | 0 | 0 | 0 |
| overall_bounce_rate_pct | 0 | 0 | 0 | 0 |
| overall_delivery_rate_pct | 0 | 0 | 0 | 0 |
| overall_health_score | 1 | 1 | 1 | 1 |
| primary_recommendation | 0 | 0 | 0 | 0 |
| recent_delivery_rate_pct | 0 | 0 | 0 | 0 |
| successful_deliveries | 0 | 0 | 0 | 0 |
| system_volume_classification | 0 | 0 | 0 | 0 |
| total_bounces | 0 | 0 | 0 | 0 |
| total_campaigns | 0 | 0 | 0 | 0 |
| total_email_attempts | 0 | 0 | 0 | 0 |
| total_leads | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：score_weights,recommendation_wording；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- score_weights：A；主项。契约只说四项阈值加权，未给分值；agent与gold不同权重。（行减少0，格减少1）
- recommendation_wording：A；主项。契约只用自然语言re-engage leads说明，没有指定完整字面标签。（行减少0，格减少1）

## 规则问题

契约“weighted composite”和业务建议没有给分值/精确输出字串。可将笼统描述解释为隐含gold实现（C），本轮按A：不借gold补契约。运行时间戳键按第7节共同固定，未把时间漂移算单独修复。
