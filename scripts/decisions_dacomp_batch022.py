from review_dacomp_batch022 import *
import hashlib,datetime,re,collections
plans=json.loads((REC/'022_patch_plan.json').read_text());q=json.loads((REC/'022_queries.json').read_text())+json.loads((REC/'022_queries_retry.json').read_text())
notes={
0:'只有STRING_AGG(DISTINCT)无序串接的元素先后不同。契约明确不保证顺序；对留存两侧只规范化该串接序列后，包含评测键的整表L0一致。',
1:'无邮件发送的376个lead在rfm_segment和next_best_action各有一处差异。前者违背明确Unknown默认；后者agent按“无打开→Welcome Series”，gold对缺失聚合的NULL落到Standard Campaign Flow。两项单修行数不变、各减376格，C/O并列。',
2:'与int_marketo__lead相同的无序串接差异；其余所有列、键及行多重性经规范化诊断一致。',
3:'原评测时间戳键遮住payload。共同固定到gold留存时刻后仅health score和recommendation文案不同；契约没有给四项具体分值或完整文案，两项均A。',
4:'email_send_id采用原id还是四列MD5未在契约定义。agent核查过跨活动ID缺乏关联，明确披露了选择；不能用gold的hash作为正确映射的依据。',
5:'gold多保留1条空白campaign_name，契约显式delete_row；agent过滤符合契约。',
6:'utils日历到今天或下周相差7行；搜索完整data_contract未发现该表的业务定义，依赖配置只列模型。差异取决于未定日历终点。',
7:'NULL account_id在MD5中补空串或0的选择导致219行变成双侧独有键（438规模）；遗漏388条CTA为另一处C。主因为A，CTA为C参与因素；其他type/rate局部变动当前同口径规模未变。',
8:'按无匹配类别SUM FILTER得到NULL；契约SUM CASE ELSE 0。三列各115格，单改均不减少行数但各减少115格，三项同为C。',
9:'固定到同一留存时刻后，3条Table Statistics的短名称/全限定名称导致不同hash键。名字字符串没有规定，单项修复减少5行，为A；accuracy_score=100占位的D单修再减1行为参与因素。客户Date Range误用NULL计数可定位，但被不同键遮住，独修规模不减，不列参与因素。',
10:'五列分类SUM FILTER对空类别返回NULL，契约要求0。行数区分不了，按格子数current_liabilities与accounts_receivable各减13格并列同类C；其余三个减格的C为参与因素。',
11:'交易的subsidiary外键与left join后维表ID分别保留原值/NULL。契约未指明输出取哪一侧；维表缺失本身不能规定业务上应丢失还是保留外键，归A。',
12:'payment_ratio未按契约零分母补0（C）与vendor_activity_status固定Inactive（D），各单修104格、行数均不减，C/D并列。',
13:'starting_at含偏移文本，TRY_CAST结果NULL，过滤排空。契约明确截到秒再解释为timestamp；按该规则单修后2230行L0完全一致，C而非U。',
14:'遗漏contract指定的customer_insights对behavior的第二次连接，单补该连接恢复44行的多重性，减少1078格；另外频率NULL/0为C、简短/长标签为O、未指定具体权重为A。按格子选连接遗漏C为主因。',
15:'波动率用score*0占位，契约要求standard deviation；13个单观测分组gold为NULL，恢复stddev_samp后L0一致。未找到agent对单观测stddev作数据判断的文字，依D。',
16:'department_revenue无Income时用NULL而非契约0，后续IS NOT NULL排掉585行并改变窗口分母；单改收入默认恢复行但暴露其他不同列，行规模不减，格子大幅减少。净利率零分母NULL/0单修也减格，C参与因素。class遗漏与其他候选本批单修不减，不计参与因素。',
17:'最终SQL直接透传另一个transaction_details模型，省去契约的源表和INNER subsidiaries连接。未找到误认为源数据缺失的判断。仅补subsidiary INNER连接便从700行到gold空表，按D。',
18:'contract_recommendation固定Standard purchase agreement，未执行合同给定supplier_tier分档；恢复该表达式52行差异清零，D。',
19:'原internalid和按longname排序生成row_number均唯一，契约未给生成规则；不能据gold选排序号否定原标识。单换编号L0一致，A。',
20:'raw accounts无两布尔列，契约没有派生公式；gold从accttype分类推导，agent NULL。按v2“原始表根本没有对应列、填法未规定”归A。',
21:'生成器已有class映射；因契约源表名与实际库不同先填全NULL，修复FROM后未刷新投影。显式映射意图与留存SQL不一致，I；不是无依据地推测想法。',
22:'同上：有完整exchange-rate列映射，event25只修FROM而保留NULL投影，I。',
23:'gold仅用@/点位置弱校验，保留two@@signs.com、missing@.com；agent按契约正则置NULL。改单处为gold弱校验后L0一致，O。',
24:'生成器明列entity_id=id等映射；修复源名后仍NULL并被ID过滤成空。主导空表来自投影未刷新，I。附带entity_name映射意图的旧名称不同不影响本次主因证据。',
25:'gold对带偏移时间直接TRY_CAST全部NULL，且cohort_month输出TIMESTAMP而契约DATE。agent正确解析得到4个月份；只改gold解析后仍有DATE/TIMESTAMP键差，再按契约DATE投影后复核一致。两项都是gold条件差异，归O；不是因agent额外WHERE就直接定C。',
26:'契约复合primary_key，agent去重；gold多4行。仅撤QUALIFY后L0一致，O。',
27:'时间解析策略A主导7981个共同键差异；额外19条重复记录来自agent执行primary_key而gold保留。按本表行尺度去重单修不减（8000→8000），因此O不列参与因素，详列为非贡献差异。',
28:'契约contact_id主键；agent4994行，gold8000行，撤去重后全表L0一致，O。',
29:'两列时间戳解析格式未规定，agent格式解析、gold直接TRY_CAST得到NULL；各单改1000格，同类A。',
30:'四列时间戳解析格式未规定，四个单项各改3000格，同类A。',
31:'复合主键去重4行，撤QUALIFY全表L0一致，O。',
32:'question_id/key主键去重4494行，撤QUALIFY全表L0一致，O。',
33:'response_id/question_id主键去重11行，撤QUALIFY全表L0一致，O。',
34:'question_id/key主键去重307行，撤QUALIFY全表L0一致，O。',
35:'last_activated_at/last_modified_at两列各6000格解析差异，契约未指定偏移解析表达式，同类A；last_accessed_at及去重单修无贡献。本表是survey，不是试标survey_version。',
36:'response_id/key主键去重2行，撤QUALIFY全表L0一致，O。',
37:'契约先LOWER(TRIM)再邮箱验证；gold先验证原文而丢弃5个带空格邮箱。agent按契约顺序；变更验证对象后L0一致，O。'
}
levels={0:3,1:3,2:3,3:4,4:1,5:2,6:1,7:4,8:4,9:3,10:4,11:4,12:4,13:2,14:4,15:4,16:3,17:4,18:4,19:3,20:3,21:3,22:3,23:3,24:3,25:1,**{i:2 for i in range(26,38)}}
labels={1:'针对本表的具体说明',2:'只有通用策略说明',3:'看到了但没提',4:'没有迹象'}
quotes={
4:'原始活动表没有独立 `email_send_id`，发送表使用 `id` 映射；其他活动表也按原始活动 ID 输出 `email_send_id`。源数据未提供可确认的跨活动发送键，因此打开、点击、投递等跨事件连接存在来源标识的局限，计数仍按 contract 在各活动自身分组。',
5:'依据 staging 契约去除缺少关键 ID/时间/必需属性的行，并对重复主键保留更新时间较新的记录（活动重复时保留较早记录）。这保全了声明的唯一粒度，但剔除记录不会进入后续分析。',
6:'日历延伸至当前日期，并按 lead created date 起算。',
13:'采用 TRY_CAST 安全解析原始日期/类型；不可解析的值成为 NULL。',
25:'无法按已观察到的带时区格式解析的日期仍保留在原文本字段，但不进入 cohort、30 日窗口及按日统计，可能造成日期类指标低估。'
}
dupquote='重复主键记录按主键仅保留一条；合同未指定冲突记录排序规则，因此非主键字段冲突时，具体保留行不保证业务优先级，可能丢失冲突值。'
timequote="原始 Qualtrics 时间文本带时区后缀（例如 `+0800`），DuckDB 直接 `try_cast(... AS TIMESTAMP)` 无法解析。日期相关 SQL 改用 `try_strptime(..., '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP`；不可解析日期在日期计算中排除。"
for i in range(26,38):quotes[i]=timequote if i in [27,29,30,35] else dupquote if i!=37 else '缺失/无效关键 ID 及合同要求删除的非法状态、邮箱或必需字段记录予以剔除；非关键无效值置 NULL。'
events={0:[13,14],1:[45,46],2:[13,14],3:[],4:[17,18,21,22,55],5:[55],6:[55],7:[],8:[],9:[33,34],10:[],11:[],12:[],13:[65],14:[],15:[],16:[53,54],17:[],18:[],19:[11,12],20:[13,14,15],21:[11,12,23,24,25],22:[11,12,23,24,25],23:[53,54,55],24:[11,12,23,24,25],25:[55,56,57,58,69,70,79],**{i:[79] for i in range(26,38)}}
rules={
3:'契约“weighted composite”和业务建议没有给分值/精确输出字串。可将笼统描述解释为隐含gold实现（C），本轮按A：不借gold补契约。运行时间戳键按第7节共同固定，未把时间漂移算单独修复。',
7:'coalesced account_id未写默认值；A（空串/0约定）与C（把gold的0看作默认）两读法。本轮A，不从gold补默认常量；缺CTA独立C。',
9:'table_name可读作全限定源表名（C）或未规定展示名（A）。契约没有字面赋值，按A；精确时间戳取gold留存列并共同控制所有运行，不归标签修复收益。',
11:'“associated with transaction”的ID可取驱动外键或joined维表键。A与C（将from joined tables理解为必须取维表）都可读；选A，未将维表匹配失败推断为U。',
14:'grain写一行/customer，但business_logic明示两次按customer_id连接，会放大多subsidiary记录；按明确可执行连接规定判遗漏C，不自行删除第二次连接。',
20:'raw无布尔列时A与D/I边界：event15注释说flags lookup，后续未落地；但契约从未定义分类映射，按第3节无对应列的A，不以gold的金融分类作为唯一正确解。',
21:'U（误判列不存在）、D（NULL占位）与I（修表名漏投影）边界：event15有正确列映射，event24报错，event25明确修源名，最终投影仍旧。因此选I，以代码证据支撑意图。',
22:'同classes：明确映射意图与只改FROM的修复代码同时存在，选I；恢复映射组视为修一个schema lookup/生成阶段问题，不把每个NULL列当独立无关选择。',
24:'同classes，选择I。entity_name旧映射entityid与实际entitytitle另有差别；本次导致0行的主导机制是ID投影仍NULL，不能把整体恢复作为每一列映射独立正确的证明。',
25:'O与A边界：契约明确首次响应月份及DATE键，gold解析全部NULL且类型TIMESTAMP；有原始日期可解析的诊断，按O。给gold改解析并cast DATE是诊断，不冒充agent单改。',
27:'同一张表行口径能选主因时，不把只减少格子、行规模不减的去重差异另列参与因素；保留单改完整数字供复核。'
}
allout=[];traces=[]
for i,r in enumerate(inventory()[:38]):
 d=json.loads((REC/('022_reruns_'+r['task']+'_'+r['table']+'.json')).read_text());base=d['runs'][0]['comparison']['levels'][0];scores=[]
 for patch in plans[i]['patches']:
  run=next(x for x in d['runs'] if x['label']==patch['label']);a=run['comparison']['levels'][0];scores.append({**patch,'row_reduction':base['row_scale']-a['row_scale'],'cell_reduction':base['cell_scale']-a['cell_scale']})
 if i in [0,2]: main='O';selected=[];factors=[];metric='行';best=None
 else:
  best=max((x['row_reduction'] for x in scores),default=0);winners=[x for x in scores if x['row_reduction']==best]
  metric='格子' if len(winners)>1 or best==0 else '行'
  if metric=='格子':best=max(x['cell_reduction'] for x in winners);winners=[x for x in winners if x['cell_reduction']==best]
  selected=[x['label'] for x in winners];cats=set(x['category'] for x in winners);main=next(iter(cats)) if len(cats)==1 else '多因并列'
  factors=[{'label':x['label'],'category':x['category']} for x in scores if x['label'] not in selected and x['row_reduction' if metric=='行' else 'cell_reduction']>0]
 n=int(r['task'][-3:]);root=ROOT/f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/{r["task"]}/agent';eventfiles=sorted(root.glob('.events/sessions/*/events/*.json'),key=lambda p:int(p.stem));data=[(p,json.loads(p.read_text())) for p in eventfiles]
 final=next(e['args']['final_thought'] for p,e in data if e.get('action')=='finish')
 quote=quotes.get(i,'');assert not quote or quote in final,(i,quote)
 trace={'index':i,'task':r['task'],'table':r['table'],'all_events_reviewed':len(data),'truncated_observation_events':[e['id'] for p,e in data if e.get('observation') and re.search('truncat',e.get('content',''),re.I)],'events':[{'id':e['id'],'path':str(p.relative_to(ROOT)),'kind':e.get('action') or e.get('observation')} for p,e in data if e['id'] in events[i]],'quote':quote,'uncertainty':labels[levels[i]],'limitation':'只依据留存动作/观察/最终报告；不把程序读取YAML当作agent看过全部内容，不推断未留存思考。'}
 traces.append(trace)
 allout.append(dict(index=i,**r,main=main,selected=selected,factors=factors,metric=metric,scores=scores,reason=notes[i],confidence='中' if main in ['A','多因并列'] or i in [20,24,25] else '高',uncertainty=labels[levels[i]],quote=quote,events=events[i],verification_count=sum(x['index']==i for x in q),rule_issue=rules.get(i,'无。按v2冻结定义执行。'),flags=['已披露'] if i==9 else []))
(REC/'022_decisions.json').write_text(json.dumps(allout,ensure_ascii=False,indent=2)+'\n');(REC/'022_trace_audit.json').write_text(json.dumps(traces,ensure_ascii=False,indent=2)+'\n');print(collections.Counter(x['main'] for x in allout));print(collections.Counter(x['uncertainty'] for x in allout));print('queries max',max(x['verification_count'] for x in allout))
