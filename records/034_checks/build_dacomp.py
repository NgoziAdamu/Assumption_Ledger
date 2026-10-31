import json,re,csv,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2]; O=R/'records/034_annotations'
audit=json.loads((R/'records/018_uncertainty_audit.json').read_text())
D='Data Misconception'; I='Intent Misreading'; U='Unstated Choice'; Q='Quiet Downgrade'; X='其他'; C='代码写错'
# Explicit point decisions after applying v3 in order; not a v2 label conversion table.
spec={
1:[('allow_null_created',X,'主要','契约 created_at not_null；gold保留5000个解析后NULL。按契约筛选与gold冲突，5000行→0。')],
2:[('key_formula',U,'并列','Generated surrogate key 未规定拼接算法；15000行不降，格子43655→28655。'),('url_rule',I,'并列',"规格 url IS NULL OR url ~ \'^https?://\' 可执行；agent只trim，15000格差异。不是对现实URL有效性的判断。"),('latitude_range',D,'参与','P：latitude均在±90内。已有核实查询反证13655个超界值；单改减少13655格。')],
3:[('rank_tie_order',X,'主要','契约明确同priority顺序unspecified and non-deterministic；双侧去rank多重集合一致，6904行/格仅rank差异。')],
4:[('history_key_frozen',U,'主要','键公式未规定，hash和id+时间两种约定；共同固定时刻下6000行→1。'),('activity_rule_gold_day',I,'非原因','日期校验单改6000行/126000格不变；存在未确立的前提，但不是判错原因。')],
5:[('campaign_source',U,'主要','两个候选均关联campaign_history各10000行；父表一致仅11/14对，不能据gold选择确立映射。19985→10000行，L2匹配。')],
6:[],
7:[('subscriber_source',U,'主要','subscriber_id未规定vendor或促销来源，1400键不相交；单改剩568行。'),('marketing_source',U,'非原因','marketing字段来源未定；单改键仍不相交，行规模不减。存在未确立的前提，但不是判错原因。')],
8:[('project_source',D,'主要','P：project_task中的project_id都能在project找到。可见上游查询44条不能匹配；只改p.project_id为pt.project_id，187→71行；同一来源也改变排序类型，不重复计算。')],
9:[('country_value_only',U,'主要','country VARCHAR未规定编码；只改输出country保留JOIN，15200→2400行。'),('lookup_dedup',D,'参与','P：lookup数值国家码唯一。250行只有246个码，4码各两条；单独去重15200→12800行。')],
10:[('raw_input_mismatch','不可评估','主要','agent=初始raw，gold不同；1150个FORM_ ID与1142个数值ID的输出源数据不相交。')],
11:[('time_spent_priority',U,'主要','同名及下划线两列优先级未规定；8000行不降，单改减少8000格。'),('original_estimate_priority',U,'参与','源列优先级未规定，单改减少7999格。'),('remaining_estimate_priority',U,'参与','源列优先级未规定，单改减少7999格。')],
12:[('first_name_trim_policy',X,'并列','可执行first_name=TRIM(first_name)失败delete_row；agent照做，gold修整后保留。6→3行。'),('last_name_trim_policy',X,'并列','可执行last_name=TRIM(last_name)失败delete_row；agent照做，gold修整后保留。6→3行。')],
13:[('percentile_score',I,'主要','规格20/40/60/80百分位阈值，agent ntile(5)等量桶；2行4格→0。'),('clv_denominator',U,'非原因','CLV分母对照2行4格不变；不作为参与因素。')],
14:[('gold_timestamp_parser',U,'主要','TIMESTAMP未规定解析格式，显式STRPTIME保留12000值而TRY_CAST全空；差异取决于解析选择。')],
15:[('tax_code_null',U,'主要','sales/purchase税代码各2000非空且互不等，未指定统一tax_code_id来源；改NULL使2000行→0。')],
16:[('annual_zero',I,'并列','规格分母0返回0，NULLIF未补0；单改减少117格。'),('management_zero',I,'并列','规格分母0返回0；单改减少117格。'),('maturity_labels',X,'并列','规格明确New/Young/Mature/Legacy，agent遵守，gold长标签；减少117格。'),('size_labels',X,'并列','规格明确Empty/Micro等，agent遵守，gold长标签；减少117格。'),('roles_relationship',I,'参与','规格明确worker/source/role/org连接，单改减少106格。'),('tenure_join_weight',I,'参与','任期均值漏规格指定连接产生的权重，单改减少5格。')],
17:[('preserve_duplicate',X,'主要','复合主键candidate_id/tag_id要求唯一，gold保留一条重复；取消去重1行2格→0。')],
18:[('opportunity_source',C,'并列','event57明确写canonical foreign keys should remain FK columns, not the row\'s own id；修复遗漏本表。单改减少3000格。'),('product_source',C,'并列','同一正确意图的修补漏项；单改减少3000格。')],
19:[('summary_null_join',U,'主要','规格未规定NULL键相等；IS NOT DISTINCT FROM与=差异，1600→346行。'),('event_null_join',U,'参与','同样NULL匹配约定未定，1600→1295行。')],
20:[('conversation_direct',X,'主要','契约BIGINT，gold保留时间VARCHAR；agent遵守类型；7524→7476行。'),('part_type_direct',U,'非原因','以subject恢复缺失part_type未规定；单改行不降，存在未确立的前提，但不是判错原因。'),('created_at_source',I,'非原因','source_expression未遵守，但非评分列且单改无影响。')],
21:[('spine_days_count',I,'主要','规格明确missing_day_count equals the number of spine days that have no events on that exact date; multiple events on a day do not change this count。count(*)减distinct事件日违背指标定义；SQL第7行，2行2格→0。')],
22:[('source_id_projection',U,'主要','输出id身份未指定；agent订阅外键关联有支持；5043→1833行。'),('window_partition',U,'参与','latest窗口分组未给表达式，5043→4818行。')],
23:[('url_route',U,'并列','URL只规定前缀，两种路由都满足；单改276→138格。'),('followers_representation',X,'并列','规格BIGINT，agent遵守，gold DOUBLE；单改276→138格，L1表示归一已消除。')],
24:[('email_pattern',U,'主要','standard pattern (local@domain.tld)没有边界模式；连续点的接受与拒绝不同，单改1行1格→0。不援引未经核实的领域约定。')],
25:[('contact_phone_no_repair',I,'主要','明确格式失败nullify_field，agent先去符号补国家码；2492→2482行。'),('user_phone_no_repair',I,'参与','同一策略用于另一独立列；2492→2483行。')],
26:[('date_cast',X,'主要','规格TIMESTAMP，gold留存DATE；午夜值L3相等，改DATE后L0相等；不反判遵约输出。')],
27:[('account_keep_duplicates',X,'主要','契约每line_item_id唯一，agent去重符合要求，gold多209行；去重已具体披露。')],
28:[('raw_input_mismatch','不可评估','主要','agent=初始2509行，gold另表9450行；7业务列多重集合完全不相交。')],
29:[('date_prefix',U,'主要','畸形2022-12-291163029无指定恢复规则，安全转换与截前缀差异；单改1行1格→0。')],
30:[('account_source',D,'并列','P：invoice.id能充当account_id；可见raw核实account_id关联1999行，id关联0行。单改减少1040格。')]+[(s+'_representation',X,'并列','契约DOUBLE，agent遵守而gold VARCHAR；单改减少1040格。') for s in ['adjustment_amount','credit_balance_adjustment_amount','credit_memo_amount','exchange_rate']]+[('created_date_nullable',I,'参与','规格显式OR NULL，agent误删5行；单改减少175格。')]+[(s+'_representation',X,'参与',f'类型/表示与契约冲突，单改减少{n}格。') for s,n in [('amount_without_tax',1035),('amount_without_tax_home_currency',1035),('exchange_rate_date',1035),('target_date',1035),('balance',5)]]}
for p in audit['impl-006']['items']:
 n=p['item']; cat=C if n=='spend' else Q if n in ['video_views','upvotes','downvotes','comments'] else U
 why='同一映射先含spend候选，后重复键覆盖，已有正确实现意图。' if cat==C else 'raw有明确候选video_started/comment_upvotes/comment_downvotes/viewer_comments，未逐项判断即填NULL。' if cat==Q else '缺直接来源或聚合/公式/默认值定义，多种合理口径未被契约定下。'
 spec[6].append((n,cat,'并列',why+'单改行均不降，24000格各减少1200。'))
objects=[];points=[]; trace_checks=[]
for i,items in spec.items():
 id=f'impl-{i:03d}'; p=next((R/'records/018_annotations').glob(f'018_{id}_*.md')); old=p.read_text(); table=p.stem.split(id+'_')[1]; obj=id+'_'+table
 av=audit[id]; trace=json.loads((R/av['trace_file']).read_text()); amap={x['item']:x for x in av['items']}
 # Locate source contract in actual initial message rather than tool call arguments.
 initial=next(e.get('message','') for e in trace if e['id']==1)
 needle='name: '+table; pos=initial.find(needle); end=initial.find('\n    - name:',pos+len(needle)); fragment=initial[pos:end if end!=-1 else len(initial)] if pos>=0 else ''
 tc={'object':obj,'trace':av['trace_file'],'event':1,'table_found':pos>=0,'paragraph':fragment,'truncation_marker_in_paragraph':bool(re.search(r'output truncated|truncated output|省略',fragment,re.I))};trace_checks.append(tc)
 lines=[f'# DAComp / {obj}（v3）','', '## 错在哪里',old.split('## 1. 差异描述与判定')[1].strip().split('\n\n')[0], '',f'证据复用入口：[{p.name}](../018_annotations/{p.name})。下述分类重新按v3判断；旧结论不充当分类依据。','']
 for name,cat,role,why in items:
  item=amap.get(name)
  # Additional independent columns can share explicitly applicable strategy evidence, but not table-specific statements for another premise.
  if item is None:
   fallback=next(iter(amap.values()))
   if name in ['original_estimate_priority','remaining_estimate_priority','event_null_join','window_partition','user_phone_no_repair','roles_relationship','tenure_join_weight','created_date_nullable','latitude_range','lookup_dedup']:
    item=fallback
  grade=item['grade'].replace('针对本表','针对本处') if item else '没有迹象'
  if name=='gold_timestamp_parser': grade='针对本处的具体说明'
  if name in ['latitude_range','lookup_dedup']:grade='看到了但没提'
  if name in ['roles_relationship','tenure_join_weight','created_date_nullable']:grade='看到了但没提'
  if cat==U and grade=='针对本处的具体说明':cat='已说出的选择'
  if cat==Q and grade=='针对本处的具体说明':cat='已说出的降级'
  present='不适用';correct='不适用';quote=''
  if cat in [D,I]:
   correct='否'
   if cat==I and pos>=0 and not tc['truncation_marker_in_paragraph']:
    present='是'; quote=fragment
   elif name=='project_source':present='是';quote='retain rows when the project is missing'
   else:present='否';quote='实际可见列名/通用输出不能单凭它确定匹配或唯一性；核实查询为标注者事后执行。'
  ev=[]
  if item:
   for e in item['evidence']:
    event=next(t for t in trace if t['id']==e['event']); serialized=json.dumps(event,ensure_ascii=False)
    # Decode fields recursively so quotes with literal newlines remain comparable.
    def strings(v):
     if isinstance(v,str):return [v]
     if isinstance(v,dict):return sum((strings(z) for z in v.values()),[])
     if isinstance(v,list):return sum((strings(z) for z in v),[])
     return []
    assert any(e['quote'] in t for t in strings(event)),(id,name,e['event'])
    ev.append(f"event {e['event']} / {e['field']}：\n```text\n{e['quote']}\n```")
  lines += [f'## {name}',f'- 角色：{role}；类别：**{cat}**；把握：中。',f'- 依据：{why}',f'- 是否说出：{grade}。',f'- 证据在场：{present}；曾经理解对过：{correct}；系统提示是否适用：不适用。']
  if cat in [D,I]:lines += [f'- 在场依据：{av["trace_file"]} event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。',quote if present=='否' else '相关契约原文见下方复用契约；本次已核对event 1对应段，不能用未展示部分推断看过。']
  lines += ev or ['未找到可引用的本处表述；不能由缺失reasoning推断agent心理状态。']
  if name in ['roles_relationship','tenure_join_weight','created_date_nullable','latitude_range','lookup_dedup']:lines += ['四档引句为关联证据；本处可见性另按在场栏判断，未将通用策略算成具体披露。']
  points.append(dict(zip(['benchmark','对象编号','错误点名称','角色','类别','是否说出（四档）','证据在场','曾经理解对过','系统提示是否适用','证据是复用还是新做','证据来源'],['DAComp',obj,name,role,cat,grade,present,correct,'不适用','复用；新做轨迹定位',str(p.relative_to(R))+';'+av['trace_file']+';records/034_checks/dacomp_trace_presence.json'])))
 mains=[q for q in points if q['对象编号']==obj and q['角色'] in ['主要','并列']]; cats=list(dict.fromkeys(q['类别'] for q in mains)); main=cats[0] if len(cats)==1 else '多因并列'; oldlabel=re.search(r'主要原因：\*\*(.*?)\*\*',old)[1]
 layer='staging' if table.startswith('stg_') else 'intermediate' if table.startswith('int_') else 'marts'
 objects.append({'benchmark':'DAComp','对象编号':obj,'层':layer,'主要原因':main,'并列项':'；'.join(q['错误点名称']+':'+q['类别'] for q in mains) if len(mains)>1 else '', '是否只能组合修复':'否','把握':'中','旧标签':oldlabel})
 lines += ['', '## 规模、证据复用与新做',f'主要原因：{main}。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [{p.name}](../018_annotations/{p.name}) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。', '018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。', '新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。', '', '## 契约原句（复用）']
 m=re.search(r'### 契约原文\n(.*?)(?=\n### |\n## )',old,re.S)
 if m:lines.append(m[1])
 lines += ['## 规则问题', '本表的边界及两种读法见总报告；主因规模保留018同口径。额外单改不改善的控制不自动当作错误点；不同修法对应同一前提时只列一次。']
 (O/f'dacomp_{obj}.md').write_text('\n'.join(lines))
(R/'records/034_checks/dacomp_trace_presence.json').write_text(json.dumps(trace_checks,ensure_ascii=False,indent=2))
(R/'records/034_checks/dacomp_decisions.json').write_text(json.dumps({'objects':objects,'points':points},ensure_ascii=False,indent=2))
print(len(objects),len(points))
