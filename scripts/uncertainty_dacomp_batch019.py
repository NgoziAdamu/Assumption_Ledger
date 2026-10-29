"""Evidence locations and explicit per-choice v2 uncertainty judgments, based on original events."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REC=ROOT/'records';out=[]
for r in json.loads((REC/'019_package_inventory.json').read_text()):
 n=int(r['task'][-3:]);t=r['table'];root=ROOT/f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/{r["task"]}/agent'
 events=[(p,json.loads(p.read_text())) for p in root.glob('.events/sessions/*/events/*.json')];events.sort(key=lambda x:x[1]['id'])
 userp,user=next((p,e) for p,e in events if e['id']==1);finalp,final=next((p,e) for p,e in events if e.get('action')=='finish');text=final.get('args',{}).get('final_thought','');level='看到了但没提';quote=None;event=1;field='message';path=userp
 if n==1 and t in ['int_lever__posting_analytics','int_lever__posting_performance','lever__departmental_hiring_trends','lever__hiring_manager_scorecard']:
  level='针对本表的具体说明';quote='本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。'
 elif n==1 and t.startswith('stg_'):
  level='只有通用策略说明';quote='转换中无法解析的可选字段通过 `TRY_CAST` 保留为 NULL；无效必需值或不合规枚举的记录按适用合同规则过滤。'
 elif n==2 and not t.startswith('stg_'):
  level='针对本表的具体说明';quote='Several complex outputs remain simplified relative to the detailed contract: product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations; the data-quality report is summary-only; RFM account-level metrics are NULL placeholders; and advanced marts such as lifecycle insights and the executive dashboard use abbreviated/defaulted derivations.'
  if t=='int_pendo__customer_rfm_analysis':level='看到了但没提';quote=None # main text mapping not account NULL disclosure
 elif n==2 and t in ['stg_pendo__user','stg_pendo__visitor_history']:
  level='只有通用策略说明';quote='Contract-directed deletion removes unusable rows and nullification retains records while setting invalid optional values to NULL.'
 elif n==3 and t in ['customer360__phone','customer360__status','customer360__updates']:
  level='只有通用策略说明';quote='契约对来源重复记录以及部分聚合排序并未规定唯一 tie-breaker；按 DuckDB 实际行为保留未指定并列顺序，不额外引入业务假设。'
 elif n==3 and t=='int_customer360__customer_lifecycle_metrics':
  level='针对本表的具体说明';quote='生命周期模拟交易数、活动量和依赖它们的派生指标按契约使用 `random()`，因此跨次执行不保证完全可复现；执行时间字段及基于当前日期的指标同样随运行时间变化。'
 elif n==3 and t in ['customer360__customer','customer360__mapping']:
  level='只有通用策略说明';quote='中间层按契约保留源业务数据的重复记录，不对 source IDs 做全局去重。下游按这些 ID 关联时，若上游相同 ID 对应多行，可能发生行数扩增；此项属于合同指定的重复保留行为。'
 elif n==3 and t=='stg_customer360__country_codes':
  level='针对本表的具体说明';quote='country alpha-2 冲突记录通过稳定字段排序保留一条，避免唯一键重复。'
 elif n==4:
  level='针对本表的具体说明';quote='历史记录同一实体同日时间戳完全相同的并列记录，按契约定义仍可能任意选取。'
 elif n==5 and t.startswith('stg_'):
  level='只有通用策略说明';quote='源时间戳含时区偏移，使用 DuckDB `try_strptime` 解析更新时间；统计日期转换为 DATE。'
 elif n==5 and t=='google_ads__customer_acquisition_analysis':
  level='针对本表的具体说明';quote='customer acquisition 的细分/建议规则未提供完整精确规则表，channel strategic recommendation 也未规定完整优先级；已采用保守、透明的 CASE 规则。'
 if quote:
  assert quote in text,(t,quote);event=final['id'];field='args.final_thought';path=finalp;start=text.index(quote)
 else:
  msg=user['message'];start=msg.find(t);assert start>=0,t;quote=msg[start:max(start+len(t),min(len(msg),start+500))]
 if r['purpose']=='校准':level='看到了但没提' # frozen blind judgment; never revised to match 018
 out.append(dict(task=r['task'],table=t,level=level,event_id=event,field=field,path=str(path.relative_to(ROOT)),quote=quote,start_offset=start,scope='主因；参与因素另见逐表说明',visibility='引用的是原事件实际留存字段；未把索引中截断/未显示内容当作已看过。',reviewed_event_ids=[e['id'] for p,e in events]))
(REC/'019_uncertainty.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
