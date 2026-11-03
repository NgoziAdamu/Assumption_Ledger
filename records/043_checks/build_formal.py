"""将人工逐点v3.2判断与复用证据结合；只写043第二阶段文件。"""
from pathlib import Path
import collections, csv, hashlib, json, re
from formal_rules import RULES,I,U,O,D,C
R=Path('records'); K=R/'043_checks'; A=R/'043_annotations'
def load(p):return json.loads(Path(p).read_text())
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def scale(c):return [{k:l[k] for k in ['level','row_scale','cell_scale']} for l in c['levels']]
handoff=load(K/'phase1_handoff.json')
assert all(sha(p)==h for p,h in handoff['calibration_file_hashes'].items())
scope=load(R/'043_scope.json')['formal']; trace_cache={}; quote_inventory=[]
def trace(task):
    path=f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/{task}/agent/output.jsonl'
    if task not in trace_cache:trace_cache[task]=(path,{e['id']:e for pair in load(path)['history'] for e in pair if 'id' in e})
    return trace_cache[task]
def cite(task,event,field,q):
    path,es=trace(task);s=es[event]
    for k in field.split('.'):s=s[k]
    assert q and q in s,(task,event,field,q[:120])
    c={'source':path,'event':event,'field':field,'quote':q};quote_inventory.append(c);return c
def contract_quote(task,block,term):
    at=block.lower().find(term.lower());assert at>=0,(task,term)
    # 保留完整行及后续验证动作，不把规则句截断在固定字符上。
    lines=block.splitlines(keepends=True); cursor=0
    for i,line in enumerate(lines):
        if cursor+len(line)>at:break
        cursor+=len(line)
    q=''.join(lines[max(0,i-2):i+13]).rstrip('\n')
    return cite(task,1,'args.content',q)
old={r['task']+'_'+r['table']:r for r in load(R/'024_decisions.json')}
queries=[]
for f in ['024_queries.json','024_mapping_queries.json','024_extra_diagnostics.json','024_diagnostics.json']:
    for idx,q in enumerate(load(R/f)):
        if q.get('task') and q.get('table'):queries.append({'source':'records/'+f,'index':idx,**q})
catalog={o['object_id']:o for o in load(K/'evidence_catalog.json')}
rawtasks={o['task']:o for o in load(K/'raw_integrity_review.json')['task_reviews']}
levels=['交付物里针对本处说明了','交付物里只有通用说明','过程中意识到了，交付物里没提','看到了相关信息，但没有意识到的迹象','没有迹象']
deliveries={}; material_audit=[]; formal=[]; process_inventory=[]

def disclosure(task,table,label,category,block,cq):
    _,es=trace(task);finish=next(e for e in es.values() if e.get('action')=='finish');final=finish['args']['final_thought']; n=finish['id']
    tier=4;q=None;why='相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。'
    if task=='impl-023' and table.endswith('account_history'):
        if label in ['id_type','id_filter']:
            tier=1;q='`account_history.id` 在源中为 VARCHAR，但契约要求 BIGINT；不可转换的键按无效主键处理并删除。';why='点名account_history.id并说明不能转换的键被删除，只覆盖id转换/过滤。'
        else:
            tier=2;q='包含字段映射、类型转换、数据清洗、无效键/时区行过滤、指标空值处理及平台相关源表连接。';why='通用说明明确提到无效时区行过滤，没有逐项说明此表的正则边界。'
    elif task=='impl-023' and table.endswith('linkedin_posts') and label=='created_source':
        tier=1;q='LinkedIn staging 契约指定的关联源表缺少可直接匹配的 UGC 历史主键，关联历史中的 `created_time` 无匹配时为空，此类记录随后按中间层的非空时间要求排除。';why='LinkedIn staging一一对应本表，并说明历史created_time来源及缺失后果。'
    elif task=='impl-024' and table=='stg_tiktok_ads__ad_group_history' and label in ['interest_category','languages','age_groups_parser']:
        tier=3;why='event19实际比较正则分割与string_split，event39改写数组解析分支，显示对共同解析问题有替代方案意识；交付报告没有解释这一处。组级意识只覆盖CSV提取点，不推广来源常量。'
        q=cite(task,19,'args.command','for q in ["select regexp_extract_all(?, \'(^|,)(\\"(?:[^\\"]|\\"\\")*\\"|[^,]*)\', 2)","select string_split(?, \',\')"]:')
    elif task=='impl-024' and table=='stg_tiktok_ads__ad_group_history' and label=='budget':
        tier=4;why='报告的try_cast通用说明只覆盖转换，不覆盖本点BUDGET与FALLBACK_TYPE的取列差异；不把转换声明算成来源选择的披露。'
    elif task=='impl-025' and label.endswith('normalized'):
        tier=4;why='报告说明验证失败置NULL，没有说明本点先去标点补+1、把本应失败的原值改成有效电话的处理；另一张outgoing_caller_id的点名说明也不推广。'
    elif task=='impl-026' and label.startswith('conversion_'):
        tier=2;q='The raw Twitter report tables do not contain the contract’s conversion metric or conversion sale amount columns. Staging emits typed NULLs for these unavailable values;';why='raw Twitter report tables是多表概括，没有点名本表或一一对应名称；第2档。'
    elif task=='impl-026' and label=='keyword_id':
        tier=1;q='The raw keyword report does not contain `keyword_id`; that field is derived from available `keyword` text, so uniqueness beyond keyword text is not guaranteed.';why='keyword report唯一对应本表，明确说明keyword文本生成id及唯一性限制。'
    elif task=='impl-026' and label=='timezone_trim':
        tier=1;q='The contract requests correction of unsupported timezones without specifying a fallback; invalid timezone values are set to `UTC`.';why='时区纠正功能只对应account_history，明确指出未定fallback并说明UTC选择。'
    elif task=='impl-027' and table=='stg_xero__journal':
        if label=='processed_at':q='Raw data does not provide a processing timestamp for some entities, so `processed_at` is NULL where unavailable.';tier=2;why='some entities未点名journal，缺失processed_at填NULL只有通用说明。'
        elif label.endswith('_type'):q='Available source timestamp strings are parsed with DuckDB `TRY_CAST`; invalid timestamps become NULL.';tier=2;why='源时间字符串转换有明确通用说明，未逐表点名。'
    elif task=='impl-030' and label.startswith('source_'):
        tier=2;q='Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。';why='说明了id映射这一类做法，但未点名此表外键，也未说明关系未核实；只记第2档。'
    elif task=='impl-030' and (label.startswith('type_') or label=='refund_type'):
        if table=='stg_zuora__invoice_item' and label in ['type_balance','type_processing_type']:
            tier=1;q='合同中少量 staging 与建模字段类型不一致（例如 invoice-item 的 processing_type/金额字段）；严格按 staging 类型输出，在业务比较时对枚举做文本转换。';why='invoice-item一一对应本表，并具体说明processing_type/金额字段类型冲突，覆盖这两点。'
        else:tier=2;q='类型不匹配且不可安全解析的数据留下 NULL，不额外推断。';why='类型冲突/安全转换只有通用说明，不能把invoice-item例子推广至本表/其他字段。'
    citations=[q if isinstance(q,dict) else cite(task,n,'args.final_thought',q)] if q else [cq]
    return tier,why,citations

for obj in scope:
    oid=obj['object_id']; task=obj['task'];table=oid[len(task)+1:];prior=old[oid]
    pkg=load(f'data/024_packages_work/024_{oid}/024_{oid}.json'); blocks=pkg['contract_specification']['blocks'];block='\n'.join(b['original_text'] for b in blocks)
    contract_path=Path(pkg['contract_specification']['source_path']);contract=contract_path.read_text()
    assert all(b['original_text'] in contract for b in blocks)
    sqlpath=Path(pkg['agent_final_SQL'][0]['path']);sql=sqlpath.read_text();assert sql==pkg['agent_final_SQL'][0]['text']
    _,es=trace(task);initial=es[1]['args']['content'];assert all(b['original_text'] in initial for b in blocks),(oid,'contract truncated')
    finish=next(e for e in es.values() if e.get('action')=='finish')
    final=finish['args']['final_thought'];comments=[l for l in sql.splitlines() if '--' in l or '/*' in l];assert not comments,(oid,comments)
    deliveries[task]={'source':trace(task)[0],'event':finish['id'],'field':'args.final_thought','final_thought':final}
    material_audit.append({'object_id':oid,'contract_path':str(contract_path),'contract_sha256':sha(contract_path),'contract_blocks':blocks,'complete_in_event1':True,'agent_sql':str(sqlpath),'agent_sql_sha256':sha(sqlpath),'sql_comments':comments,'gold_sql':pkg['gold_SQL_仅供定位差异'][0]['path']})
    oq=[q for q in queries if q['task']==task and q['table']==table]
    vq=[q for q in oq if q['kind']=='核实'];assert len(vq)<=5,(oid,len(vq))
    raw=catalog[oid]['raw_direct_sources']
    raw_note='staging采用agent留存raw；013直接源对照逐项列出。' if obj['layer']=='staging' else 'CS口径：输入使用gold上游，只评估本表自己；不把本题raw差异直接归到本表。'
    if task=='impl-025':raw_note+=' 013的call/message变化在015的gold raw中也有；本表仍照常评估。'
    if task=='impl-030':
        if obj['layer']=='staging':
            changed=any(x['013_different'] for x in raw)
            raw_note=('本表早期源检查处于坏结构（原始单列、header挤在列名中）；最终执行用正常展开结构。' if changed else '本表直接raw源初始就为正常多列结构，最终执行仍为正常多列结构。')
            raw_note+=' event19生成SQL时已见初始结构；event31运行原版run.py导入raw，event40确认展开后的列清单，event45的最终映射生成发生在此后。'+('本表展开列数见直接源对照。' if changed else '')
        else:raw_note='本表最终SQL执行时Zuora库内raw已为正常多列（invoice为54列），但本次CS输入直接使用gold上游。早期检查的invoice单列坏结构不作为本表CS输入。'
        raw_note+=' 初始与agent的run.py SHA-256相同，event10已展示单列按逗号拆分导入逻辑；不是agent另写修复原库。015确认gold与agent raw一致。正常结构不代表所有字段内容位置都符合语义，需逐列核实。'
    record={**obj,'table':table,'old24_main':prior['category'],'contract_path':str(contract_path),'sql_path':str(sqlpath),'package':f'records/024_packages/024_{oid}.md','raw_direct_sources':raw,'raw_note':raw_note,'verification_queries':vq,'diagnostics':[q for q in oq if q['kind']=='诊断'],'points':[],'rule_questions':[]}
    if task=='impl-028' and obj['layer']=='staging':
        record.update(main='不可评估',confidence='高',combination_only=False,ranking_note='不进行机制归因或五档统计。',unevaluable_sources=['records/013_raw_impl-028.json','records/015_raw_impl-028.json','records/024_diagnostics.json'])
        record['raw_note']='agent留存与initial直接raw内容差集为0；gold读取另一组名称、schema和行数不同的raw。按第6节不可评估；不将此结论推广到int_youtube__video。'
        formal.append(record);continue
    for patch in prior['patches']:
        label=patch['label'];f=patch['record'];runs=load(f);r=next(r for r in runs['runs'] if r['label']==label);b=next(r for r in runs['runs'] if r['label']=='baseline')
        assert 'comparison'in r
        if label in RULES.get(table,{}):category,reason,term=RULES[table][label]
        elif task=='impl-023' and table.endswith('twitter_user_history') and label.startswith('type_'):
            col=label[5:];category=O;reason=f'{col}契约为BIGINT，agent按类型转换，gold保留DOUBLE；不是只凭gold值定义应输出什么。';term='name: '+col
        elif task=='impl-026' and label=='date_type':category=O;reason='本表date_day契约明确TIMESTAMP，agent照做；gold为DATE。评测键不做日期容差，不能把符合契约的timestamp当作形式错误。';term='date_day'
        elif task=='impl-026' and label.startswith('conversion_'):
            category=U;reason=f'raw列清单没有{label}对应列；契约未指定缺失填0还是NULL，agent留类型化NULL，不能归Quiet Downgrade。';term=label
        elif task=='impl-026' and label=='keyword_id':category=U;reason='raw无keyword_id，契约没定生成公式；keyword文本与gold组合MD5是键值生成选择，不是纯形式。';term='keyword_id'
        elif task=='impl-027' and table=='stg_xero__invoice_line_item':category=O;reason=f'{label}契约明确DECIMAL(18,2)，agent照做，gold保留DOUBLE/更多精度。';term='name: '+label
        elif task=='impl-030' and (label.startswith('type_') or label=='refund_type'):
            col=label[5:] if label.startswith('type_') else 'refund';category=O;term='name: '+col
            reason=f'{col}在本表契约中有明确类型，agent依其转换；gold透传raw的不同类型/表示。不是把gold的转换失败当作数据事实。'
        elif task=='impl-030' and label.startswith('source_'):
            col=label[7:];term='name: '+col
            fm=next(q for q in vq if q['label']=='外键字段格式诊断（原可见数据）');ma=next(q for q in vq if q['label']=='实际纳入行的候选映射')
            fmt=next(dict(zip(fm['columns'],row)) for row in fm['rows'] if row[0]==col);match=next(dict(zip(ma['columns'],row)) for row in ma['rows'] if row[0]==col)
            # 直接证据：非空候选全为一致ID格式、确有目标匹配，而所选实体id完全无匹配。
            clear=(fmt['nonnull']>0 and fmt['hex32']==fmt['nonnull'] and match['chosen_matches']==0 and match['named_matches']>0)
            category=D if clear else U
            reason=(f'P：本表实体id可作为{col}对应目标实体的关系键。实际纳入{match["n"]}行，所选id匹配{match["chosen_matches"]}，具名{col}匹配{match["named_matches"]}；非空候选{fmt["nonnull"]}个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。' if clear else f'契约未给{col}来源映射；实际纳入{match["n"]}行，所选id匹配{match["chosen_matches"]}、具名列匹配{match["named_matches"]}，非空{fmt["nonnull"]}中ID格式{fmt["hex32"]}、时间文本{fmt["timestamps"]}。候选内容错位、无对应或反向匹配，不能由gold选列确立唯一语义，按Unstated Choice。')
        else:raise AssertionError((oid,label,'missing manual rule'))
        # 契约项真正存在，且逐表完整出现在初始消息中。
        if term.lower() not in block.lower():raise AssertionError((oid,label,term))
        cq=contract_quote(task,block,term)
        tier,why,dquotes=disclosure(task,table,label,category,block,cq)
        if category==U and tier==1:category='已说出的选择'
        ep='是' if category==I else ('否' if category==D else '不适用');ever='否' if category in [I,D] else '不适用';decision_quotes=[cq]
        p={'object_id':oid,'point':label,'category':category,'confidence':'中' if category in [U,'已说出的选择'] or label in ['harmful_filter','empty_filter','published_type','window_frame'] else '高','reason':reason,'disclosure':tier,'disclosure_reason':why,'disclosure_citations':dquotes,'evidence_present':ep,'previously_correct':ever,'system_prompt':'不适用','decision_citations':decision_quotes,'source':f,'run_label':label,'baseline':scale(b['comparison']),'after':scale(r['comparison']),'edits':r['edits'],'clock_control':runs.get('clock_control',[]),'source_database':runs['source']}
        if category==D:
            p['P']=f'本表实体id可作为{col}对应目标实体的关系键。';p['verification']={'format_query':{'source':fm['source'],'index':fm['index'],'result':fmt},'mapping_query':{'source':ma['source'],'index':ma['index'],'result':match}};p['previously_correct']='是'
            p['evidence_presence_reason']='agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。'
            if table=='stg_zuora__product_rate_plan':
                p['confidence']='中';p['reason']+=' 目标覆盖仅2/505，支持该关系的匹配样本稀疏，因此把握为中；不另设类别最低匹配率门槛。'
        if task=='impl-030' and label.startswith('source_'):
            p['decision_citations'] += [cite(task,19,'args.command',"srcname=n\n            e=f'try_cast(\"{srcname}\" AS {typ})'"),cite(task,45,'args.command',"if n in pk_alias: srcname='id'")]
            p['process_note']='同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。'
            p['mapping_evidence']={'format':fmt,'matching':match}
        if task=='impl-028' and label.endswith('_regex'):
            p['decision_citations'].append(cite(task,29,'args.command',r['edits'][0]['old']))
        if label in ['harmful_filter','empty_filter','window_frame'] or table=='stg_tiktok_ads__ad_group_history' and label=='age_groups_parser' or label=='published_type':record['rule_questions'].append({'point':label,'reason':reason})
        b0=p['baseline'][0];a0=p['after'][0];p['reduction']=[b0['row_scale']-a0['row_scale'],b0['cell_scale']-a0['cell_scale']]
        record['points'].append(p)
    # 允许并列顺序的逐列原因：旧证据只做成组诊断，不编造单改单列收益。
    if table in ['social_media_reporting__rollup_report','xero__invoice_line_items']:
        diag=next(q for q in oq if q['label']=='排除并列顺序派生列后的整表诊断')
        for col in diag['excluded']:
            term='ties get arbitrary order' if task=='impl-023' else 'their relative order is unspecified'
            cq=contract_quote(task,block,term)
            record['points'].append({'object_id':oid,'point':col,'category':O,'confidence':'中','reason':'契约允许并列键的任意行次序；024诊断核对并列组及排除相应派生列后的其他内容。该列单独列点，但没有独立单改收益，不用成组清零冒充该列清零。','disclosure':4,'disclosure_reason':'event1完整看到允许并列规则；交付报告没交代本处，写窗口实现不等于意识到另一个合法顺序。','disclosure_citations':[cq],'evidence_present':'不适用','previously_correct':'不适用','system_prompt':'不适用','decision_citations':[cq],'source':diag['source'],'run_label':diag['label'],'baseline':scale(prior['baseline']),'after':None,'group_diagnostic':{'index':diag['index'],'excluded':diag['excluded'],'levels':scale(diag['comparison']),'tie_details':diag.get('tie_permutations',diag.get('tie_groups'))},'reduction':None,'role':'同类候选'})
    ps=record['points'];improved=[p for p in ps if p['reduction'] is not None and tuple(p['reduction'])>(0,0)]
    combos=[q for q in oq if q.get('label')=='多处组合仅诊断（不用于单点原因排名）']
    same_unranked=any(p['reduction'] is None for p in ps)
    if same_unranked:
        assert {p['category'] for p in ps}=={O}
        record.update(main=O,confidence='中',combination_only=False,ranking_note='手册第7节同类候选例外：全部候选均其他，但并列顺序点只有组级诊断，未逐项排序。旧数值单改列原数字，不能与没有单改的点伪造完整名次。')
        for p in ps:p['role']='同类候选'
    elif improved:
        best=max(tuple(p['reduction']) for p in improved);main=[p for p in improved if tuple(p['reduction'])==best];cats=sorted({p['category'] for p in main})
        record.update(main=cats[0] if len(cats)==1 else '多因并列',main_points=[p['point'] for p in main],confidence='中' if any(p['confidence']=='中' for p in main) else '高',combination_only=False,ranking_note=f'先比行减量，再比格减量；最大减量为{best[0]}行/{best[1]}格。行增多时即使格减少也不作为改善。')
        for p in ps:p['role']=('主要' if len(main)==1 else '并列') if p in main else ('参与' if p in improved else '非原因')
    elif combos:
        combo=combos[0];record.update(main=(ps[0]['category'] if len({p['category'] for p in ps})==1 else '多因并列'),main_points=combo['labels'],confidence='中',combination_only=True,ranking_note='所有逐点单改均不减少行或格，组合减少；不将零改善点记为参与因素。',combination={'source':combo['source'],'index':combo['index'],'labels':combo['labels'],'levels':scale(combo['comparison'])})
        for p in ps:p['role']='组合项' if p['point'] in combo['labels'] else '非原因'
    else:raise AssertionError((oid,'ranking missing'))
    formal.append(record)

save(K/'formal_working.json',formal)
save(K/'formal_material_audit.json',material_audit)
save(K/'formal_delivery_sources.json',deliveries)
save(K/'formal_quote_inventory.json',quote_inventory)
save(K/'formal_query_inventory.json',[{'object_id':o['object_id'],'verification_count':len(o['verification_queries']),'queries':o['verification_queries']} for o in formal])
print('formal',len(formal),'points',sum(len(o['points']) for o in formal))
print(collections.Counter(o['main'] for o in formal))
