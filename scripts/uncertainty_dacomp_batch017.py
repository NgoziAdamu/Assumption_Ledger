"""Factual trajectory field; intentionally separate from attribution decisions."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];REC=ROOT/'records'
# Exact final-report quotations, followed by scope limits. These do not assert introspective awareness.
MENTION={
21:(41,'事件 attribution 解析按契约优先级提取 JSON 子事件 ID，查找限定同一 `source_relation`；事件重复保留且照常计数。','提到了共享事件数据的重复保留/计数策略；未讨论本表date spine连接扩行或同人同日多事件如何计算missing_day_count。'),
27:(41,'Duplicate account codes exist in source; the invoice enrichment chooses one account deterministically by lowest `account_id` to prevent duplicate output line rows. This can discard alternate account attributes for colliding codes.','明确指向本表连接去重及丢失其他账户属性的代价。'),
29:(55,'必填字段空值或转换失败的记录按契约过滤；可选字段转换失败会成为 `NULL`。重复记录、枚举和文本规范化没有超出契约进行更改。','明确声明适用于本表可选日期列的转换失败→NULL策略；没有点名1163027或其畸形日期，不能据此声称已经看过异常值。'),
30:(71,'Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。非关键不可解析值转为 NULL。','明确说明id映射选择；不等于核实本表invoice id可以当account id。类型方面另说明严格按staging类型输出，但例子不是本表。')}
OBS={
21:[(32,'staging stg_klaviyo__event')],
22:[(10,'subscription_history:')],
23:[(24,'facebook_pages_page_data')],
24:[(16,'tiktok_advertiser_data'),(50,'staging advertiser email valid/non-null:')],
25:[(16,'call_data ['),(24,'stg_twilio__call user_phone_number')],
26:[(10,'twitter_campaign_locations_report_data')],
27:[(28,'select count(*),count(distinct line_item_id)')],
28:[(22,'youtube_channel_demographics_data'),(24,'youtube_channel_demographics_data')],
29:[(18,'schedule_holiday_data:')],
30:[(40,'zuora_invoice_data')]}
LIMITS={
22:'最终报告event33谈到其他subscription字段缺失及删除标记策略；未解释本表输出id/窗口分组选择。删除标记单改无差异，不据该说明升级。',
23:'event55说明时间窗造成空表以及其他平台字段缺口，但当前选表差异已按共同日期控制，剩余URL路由/粉丝数类型未被单独讨论。',
24:'event63提到可选邮箱校验失败置NULL，但未明确两种正则接受集合的选择，也未提到双点域名。普通“做过校验”不足以证明提到本表差异的边界。',
25:'event41对outgoing_caller_id另表的非法电话有明确说明；没有说明本表call主动去符号/补+1的选择，不把另表说明迁移到本表。',
26:'event37说明缺失conversion列和其他模型歧义，但这些列不在本表评分列中；没有明确讨论本表date_day保留TIMESTAMP或改成DATE的选择。',
28:'event57说明channel_basic/video缺失字段、空video_id与run.py导入修复；没有明确讨论demographics原始表名替换或其输入与gold的差异。'}
def main():
 out={}
 for n in range(21,31):
  es=json.loads((REC/f'017_trace_impl-{n:03}.json').read_text());byid={e['id']:e for e in es};ev=[]
  if n in MENTION:
   i,quote,limit=MENTION[n];s=byid[i]['args']['final_thought'];assert quote in s,(n,i,quote)
   ev.append({'event':i,'field':'args.final_thought','quote':quote,'path':byid[i]['path']});status='已提到'
  else:status='看到了但没提';limit=LIMITS[n]
  for i,needle in OBS[n]:
   s=byid[i].get('content','');pos=s.find(needle);assert pos>=0,(n,i,needle)
   ev.append({'event':i,'field':'content','quote':s[pos:pos+1900],'path':byid[i]['path'],'excerpt_policy':'exact contiguous displayed excerpt; 1900-character cap is our excerpt, not original agent truncation'})
  out[f'impl-{n:03}']={'status':status,'evidence':ev,'scope_limit':limit,'scanned_event_count':len(es),'all_event_ids':[e['id'] for e in es], 'nonempty_archived_thought_fields':[{ 'event':e['id'],'field':k,'value':v} for e in es for k,v in [('thought',e.get('thought')),('args.thought',e.get('args',{}).get('thought'))] if v], 'method':'reviewed full event sequence and final report; command wrapper/SQL alone is not an explicit uncertainty statement; no inference about unrecorded private reasoning; does not determine attribution category'}
 (REC/'017_uncertainty_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('uncertainty',[(k,v['status']) for k,v in out.items()])
if __name__=='__main__':main()
