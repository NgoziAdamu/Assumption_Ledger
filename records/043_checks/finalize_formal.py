"""043第二阶段汇编。仅写043；不执行轨迹代码、不连接数据库。先运行build_formal.py。"""
from pathlib import Path
from collections import Counter
import csv, hashlib, io, json
R=Path('records'); K=R/'043_checks'; A=R/'043_annotations'
def load(p):return json.loads(Path(p).read_text())
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
formal=load(K/'formal_working.json'); hand=load(K/'phase1_handoff.json')
assert all(sha(p)==h for p,h in hand['calibration_file_hashes'].items())
cache={}
def events(task):
    path=f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/{task}/agent/output.jsonl'
    if task not in cache:cache[task]=(path,{e['id']:e for pair in load(path)['history'] for e in pair if 'id'in e})
    return cache[task]
def cite(task,n,q=None,field='args.command',contains=None):
    path,es=events(task);s=es[n]
    for k in field.split('.'):s=s[k]
    if q is None:q=next(l for l in s.splitlines() if contains in l)
    assert q and q in s,(task,n,q)
    return {'source':path,'event':n,'field':field,'quote':q}
def select(task,pred=lambda o:True):return [o for o in formal if o['task']==task and pred(o)]
def affected(objs,pred=lambda p:True):
    return [{'object_id':o['object_id'],'points':[{'point':p['point'],'category':p['category'],'role':p['role']} for p in o['points'] if pred(p)]} for o in objs]

# 共同生成动作全目录；不同SQL放在同一脚本不自动证明其内部逻辑相同。
families=[]
def family(fid,task,script,ids,objs,desc):
    refs=[cite(task,n,contains='cat ') for n in ids]
    f={'id':fid,'task':task,'script':script,'events':ids,'description':desc,'citations':refs,'affected':affected(objs)}
    f['table_count']=len(objs);f['point_count']=sum(len(x['points']) for x in f['affected']);families.append(f)
    for o in objs:
        assert 'generation_family' not in o
        o['generation_family']=fid
        for p in o['points']:p['generation_family']=fid
family('023-write-sql','impl-023','/tmp/write_sql.py',[29,31,33],select('impl-023'),'同一files字典脚本分三次写入staging、中间层、marts；各表表达式分别定义。')
family('024-gen-staging','impl-024','/tmp/gen.py',[23],select('impl-024',lambda o:o['layer']=='staging'),'循环读取契约与header生成staging；event25/27/29修订，event39修订数组解析。')
families[-1]['citations'].append(cite('impl-024',39,contains='s=p.read_text().replace'))
family('024-models','impl-024','/tmp/models.py',[33],select('impl-024',lambda o:o['layer']!='staging'),'agg_model批量生成marts；复制source_relation联接条件到多个模型。')
family('025-write-sql','impl-025','/tmp/write_sql.py',[17],select('impl-025'),'同一sql字典写入两张正式staging；电话标准化式重复使用，friendly_name后续独立调整。')
family('026-gen','impl-026','/tmp/gen.py',[13,17,19],select('impl-026'),'report辅助函数批量生成report staging；同一脚本追加agg_model和marts，keyword在event21修正。')
family('027-stages','impl-027','/tmp/gen.py',[19],select('impl-027',lambda o:o['layer']=='staging'),'stages字典及写文件循环生成staging；金额与时间表达式按表分别列出。')
family('027-models','impl-027','/tmp/models.py',[21,23],select('impl-027',lambda o:o['layer']!='staging'),'同一models脚本写两个正式marts；窗口和数值表达式仍逐项列点。')
family('028-staging-command','impl-028','event25 shell heredoc批量写SQL',[25],select('impl-028',lambda o:o['layer']=='staging'),'同一命令写两个正式staging，event27另作修订；原始输入与gold不同，不建立错误点或因果计数。')
family('028-video-command','impl-028','event29 shell heredoc批量写SQL',[29],select('impl-028',lambda o:o['layer']!='staging'),'同一命令写int_youtube__video及本批范围外marts；本批三段缩略图正则复制了相同转义写法。')
family('030-gen-stage','impl-030','/tmp/gen_stage.py',[19],select('impl-030',lambda o:o['layer']=='staging'),'统一按契约生成staging类型与表达式，event21/25修订，event45将pk_alias集合统一映射为本表id。')
families[-1]['citations'].append(cite('impl-030',45,contains='pk_alias='))
family('030-account-command','impl-030','event47 shell heredoc批量写SQL',[47],select('impl-030',lambda o:o['table']=='zuora__account_overview'),'同一命令写三个marts；本批仅account_overview在范围内，错误点为invoice/item INNER JOIN。')
family('030-mrr-command','impl-030','event49 shell heredoc批量写SQL',[49],select('impl-030',lambda o:o['table']=='zuora__monthly_recurring_revenue'),'同一命令写四个marts；本批仅MRR在范围内，两处非空服务日期过滤逐点记录。')
assert all('generation_family'in o for o in formal)

# 可确认同一语义/实现规则的较细归并；其余点保持独立，避免一份脚本被当作单一认识。
roots=[]
def root(rid,task,event,desc,objs,pred,refs):
    entries=[x for x in affected(objs,pred) if x['points']]
    r={'id':rid,'task':task,'event':event,'description':desc,'citations':refs,'affected':entries,'table_count':len(entries),'point_count':sum(len(x['points']) for x in entries)}
    assert r['point_count']>1
    roots.append(r)
    for o in objs:
        for p in o['points']:
            if pred(p):
                assert 'root_decision' not in p
                p['root_decision']=rid
root('024-source-relation','impl-024',23,'两个staging统一把source_relation生成为平台常量tiktok_ads。',select('impl-024',lambda o:o['layer']=='staging'),lambda p:p['point']=='source_relation',[cite('impl-024',23,contains="if n=='source_relation'")])
root('024-csv-parser','impl-024',23,'同一header索引/CSV提取生成分支读取ad_group字段；event39统一修订数组分支。',select('impl-024',lambda o:o['table']=='stg_tiktok_ads__ad_group_history'),lambda p:p['point'] in ['interest_category','languages','budget','age_groups_parser'],[cite('impl-024',23,contains='list_extract(string_split'),cite('impl-024',39,contains='s=p.read_text().replace')])
root('024-extra-source-joins','impl-024',33,'marts生成时重复附加source_relation相等联接条件。',select('impl-024',lambda o:o['layer']=='marts'),lambda p:p['point'].endswith('_source_join'),[cite('impl-024',33,contains='joins=[\'left join intermediate.int_tiktok_ads__ad_history_latest')])
root('025-phone-normalize','impl-025',17,'把原电话先去非数字字符、补+1，再检验正则；两张表三列共用写法。',select('impl-025'),lambda p:p['point'].endswith('normalized'),[cite('impl-025',17,contains='as phone_number_normalized'),cite('impl-025',17,contains='as from_normalized'),cite('impl-025',17,contains='as to_normalized')])
root('026-report-date','impl-026',13,'report辅助函数把date统一转TIMESTAMP。',select('impl-026'),lambda p:p['point']=='date_type',[cite('impl-026',13,contains='fields=["try_cast(date as timestamp)')])
root('026-report-null-conversions','impl-026',13,'report辅助函数对raw中缺失的四种conversion字段统一输出类型化NULL。',select('impl-026'),lambda p:p['point'].startswith('conversion_'),[cite('impl-026',13,contains="fields += ['cast(null as bigint)")])
root('026-mart-campaign-projection','impl-026',19,'两个marts维度投影都取li.campaign_id而非已匹配campaigns的campaign_id。',select('impl-026'),lambda p:p['point']=='campaign_projection',[cite('impl-026',19,contains='ptdims='),cite('impl-026',19,contains='udims=')])
root('027-line-numeric','impl-027',19,'invoice_line_item投影按契约对五个数值字段统一CAST到DECIMAL(18,2)。',select('impl-027',lambda o:o['table']=='stg_xero__invoice_line_item'),lambda p:True,[cite('impl-027',19,contains='TRY_CAST(discount_rate'),cite('impl-027',19,contains='TRY_CAST(quantity')])
root('028-thumbnail-escaping','impl-028',29,'三种缩略图URL正则复制同一quoted heredoc中的双反斜杠写法。',select('impl-028'),lambda p:p['point'].endswith('_regex'),[cite('impl-028',29,contains='as default_thumbnail_url'),cite('impl-028',29,contains='as medium_thumbnail_url'),cite('impl-028',29,contains='as high_thumbnail_url')])
root('030-contract-types','impl-030',19,'staging统一按契约的type处理source_expression或同名源列，生成安全类型转换。',select('impl-030',lambda o:o['layer']=='staging'),lambda p:p['point'].startswith('type_') or p['point']=='refund_type',[cite('impl-030',19,contains="e=f'try_cast"),cite('impl-030',19,contains="expr.replace('cast('")])
root('impl-030-event45-pk_alias','impl-030',45,'pk_alias集合中的外键名一律改取本表id；event19原先按正确同名列生成。',select('impl-030'),lambda p:p['point'].startswith('source_'),[cite('impl-030',19,"srcname=n\n            e=f'try_cast(\"{srcname}\" AS {typ})'"),cite('impl-030',45,"if n in pk_alias: srcname='id'")])
for o in formal:
    for p in o['points']:
        p.setdefault('root_decision',o['object_id']+':'+p['point'])
        if p['root_decision'].startswith(o['object_id']+':'):
            roots.append({'id':p['root_decision'],'task':o['task'],'event':None,'description':'未证明与其他点来自同一具体规则，保守按本点独立计。共同生成文件另见generation_families。','citations':p['decision_citations'],'affected':[{'object_id':o['object_id'],'points':[{'point':p['point'],'category':p['category'],'role':p['role']}]}],'table_count':1,'point_count':1})
def group_counts(groups):
    combos=Counter();incidence=Counter()
    for g in groups:
        cats=sorted({p['category'] for o in g['affected'] for p in o['points']})
        if cats:combos[' + '.join(cats)]+=1;incidence.update(cats)
    return {'nonempty_units':sum(combos.values()),'category_sets_mutually_exclusive':dict(combos),'category_incidence_nonexclusive':dict(incidence)}
shared={'stage':'final','scope':'50张正式表，182点；不混入校准。','counting_note':'共同生成动作目录完整覆盖50表；其中两张不可评估无错误点。按生成动作计会把同一脚本内不同逻辑并在一起，故同时给出更细的已确认同一规则归并口径。两种均只用于敏感性统计，不改变逐点类别或主要原因排序。类别集合为互斥单元，category_incidence允许一个混合单元重复出现。',
        'generation_families':families,'decisions':roots,'generation_counts':group_counts(families),'root_decision_counts':group_counts(roots)}
save(K/'shared_root_decisions.json',shared)

# raw导入时间线：只阅读原版代码和原轨迹，不运行其中命令。
initial=Path('/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/run.py')
agent=Path('/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/run.py')
assert sha(initial)==sha(agent)
raw=load(K/'raw_integrity_review.json');raw['stage']='final'
raw['zuora_timeline']={'initial_run_py':str(initial),'agent_run_py':str(agent),'sha256_both':sha(initial),'reason':'benchmark原版run.py导入raw时识别单列header并按逗号展开；agent执行pipeline触发导入，不是agent自行修改run.py修复源数据库。','citations':[
    cite('impl-030',10,contains='if len(sinfo) == 1:',field='content'),
    cite('impl-030',10,contains='header_cols =',field='content'),
    cite('impl-030',10,contains='string_split({col_ident}',field='content'),
    cite('impl-030',18,contains='stg_zuora__invoice missing direct',field='content'),
    cite('impl-030',31,contains='python3 run.py'),
    cite('impl-030',40,contains='zuora_invoice_data ',field='content')],
    'interpretation':'event18列清单检查仍是单列坏结构；event31运行已有导入程序后，event40看到正常invoice54列，event45错误外键规则生成在这之后。正常列结构不保证内容无错位。两张marts本次仍按CS用gold上游。'}
raw['per_object_final']=[{'object_id':o['object_id'],'raw_note':o['raw_note'],'raw_direct_sources':o['raw_direct_sources'],'generation_family':o['generation_family']} for o in formal]
raw['handling']='正式表已完成逐表013检查；staging使用agent留存raw。025/029/030的变化gold也有，028两个staging不可评估；029本批零正式表。'
save(K/'raw_integrity_review.json',raw)

review=load(K/'026_review_preparation.json');review['stage']='final';review['invoice_versions']=raw['zuora_timeline']
for old in review['024-1']:
    o=next(o for o in formal if o['object_id']==old['object_id'])
    old['category_pending']=False;old['main']=o['main'];old['combination_only']=o['combination_only'];old['points']=[{'point':p['point'],'category':p['category'],'role':p['role'],'reduction':p['reduction']} for p in o['points']]
review['021-2']['handling']='已逐点复核：43个source_*点中Data22、Choice21；Data点曾经理解对过均是（event19），证据在场均否。event45是主动全局映射决定，非同一字典无意覆盖，不因此归代码写错。'
review['024-2']='shared_root_decisions已补齐12个共同生成动作、具体共享规则及逐点成员；提供两种去重口径。'
review['account_history']['final']={'main':'其他','combination_only':True,'delivery_tiers':{'id_type':1,'id_filter':1,'timezone_filter':2},'reason':'契约明确BIGINT/not_null/delete-row；原始id全非数值，agent照做输出0行，不能用gold保留文本判agent误解。组合后仍11行11格，不称完整修复。'}
save(K/'026_review_final.json',review)

# CSV保留已提交的校准前缀，追加正式50张。
levels=['交付物里针对本处说明了','交付物里只有通用说明','过程中意识到了，交付物里没提','看到了相关信息，但没有意识到的迹象','没有迹象']
for typ in ['objects','points']:
    prefix=(K/f'phase1_{typ}_prefix.csv').read_text();header=next(csv.reader(io.StringIO(prefix)));s=io.StringIO();w=csv.DictWriter(s,header,lineterminator='\n')
    for o in formal:
        if typ=='objects':
            selected=[p for p in o['points'] if p['role'] in ['并列','组合项','同类候选']]
            w.writerow(dict(zip(header,['DAComp',o['object_id'],o['layer'],o['main'],'；'.join(p['point']+':'+p['category'] for p in selected),'是' if o['combination_only'] else '否',o['confidence'],o['old24_main'],o['old24_main']])))
        else:
            for p in o['points']:
                refs=[p['source'],o['package'],'records/043_checks/formal_working.json','records/043_checks/disclosure_audit.json','records/043_checks/shared_root_decisions.json']
                refs+=list(dict.fromkeys(q['source'] for q in o['verification_queries']+o['diagnostics']))
                w.writerow(dict(zip(header,['DAComp',o['object_id'],p['point'],p['role'],p['category'],levels[p['disclosure']-1],p['evidence_present'],p['previously_correct'],p['system_prompt'],'复用；043核对原始契约/交付物/轨迹',';'.join(refs),o['old24_main']])))
    (R/f'043_{typ}.csv').write_text(prefix+s.getvalue())

audit=load(K/'disclosure_audit.json');calids=set(load(R/'043_scope.json')['calibration'])
cal_audit=[p for p in audit['points'] if p['object_id'] in calids];assert len(cal_audit)==35
materials={m['object_id']:m for m in load(K/'formal_material_audit.json')};deliveries=load(K/'formal_delivery_sources.json')
for o in formal:
    for p in o['points']:
        m=materials[o['object_id']]
        cal_audit.append({'object_id':o['object_id'],'point':p['point'],'category':p['category'],'disclosure':p['disclosure'],'reason':p['disclosure_reason'],'citations':p['disclosure_citations'],'delivered_sql':m['agent_sql'],'delivered_sql_sha256':m['agent_sql_sha256'],'delivered_sql_has_comments':False,'final_event':deliveries[o['task']]['event'],'final_source':deliveries[o['task']]['source']})
save(K/'disclosure_audit.json',{'stage':'final','formal_complete':True,'objects':52,'formal_objects':50,'points':cal_audit,'unevaluable_objects':[o['object_id'] for o in formal if o['main']=='不可评估'],'rule':'只认finish final_thought或result.md及交付SQL注释；本批正式50份SQL均无注释。第3档不以写实现本身为证据。'})

# 逐表说明包含完整单改尺度和原句；校准文件不写。
fmap={f['id']:f for f in families};rmap={r['id']:r for r in roots}
def qtext(q):return f"event {q['event']} / `{q['field']}`，来源 `{q['source']}`：\n\n```text\n{q['quote'].rstrip()}\n```\n"
def sc(s):return '; '.join(f"{x['level']}={x['row_scale']}行/{x['cell_scale']}格" for x in s)
for o in formal:
    f=fmap[o['generation_family']]
    lines=[f"# 043：{o['object_id']}",'','## 结论','',f"主要原因：**{o['main']}**；把握：{o['confidence']}；只能组合修复：{'是' if o['combination_only'] else '否'}。",'',o['ranking_note'],'',f"层：{o['layer']}。024旧主要原因原样保留：`{o['old24_main']}`；旧标签不用于判类。",'','## 材料与输入','',f"契约：`{o['contract_path']}`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。",'',f"交付SQL：`{o['sql_path']}`；无SQL注释。材料包：`{o['package']}`。",'',o['raw_note'],'',f"已逐张读取 `records/013_raw_{o['task']}.json`；与gold关系见 `records/015_raw_{o['task']}.json`、`records/043_checks/raw_integrity_review.json`。"]
    for r in o['raw_direct_sources']:lines+=['',f"- `{r['source']}`：initial {r['initial_rows']}行/{r['initial_columns']}列；agent留存 {r['agent_rows']}行/{r['agent_columns']}列；013差异={r['013_different']}。"]
    lines+=['','## 同源决定','',f"同源决定：event {','.join(map(str,f['events']))}，`{f['script']}`：{f['description']} 目录编号：`{f['id']}`。共同脚本覆盖本表全部点；不改变逐点类别和排序。"]
    for rid in dict.fromkeys(p['root_decision'] for p in o['points']):
        r=rmap[rid]
        if r['event'] is not None:
            names=[p['point'] for p in o['points'] if p['root_decision']==rid]
            lines+=['',f"同源决定：event {r['event']}，{r['description']} 本表点：{', '.join(names)}；编号 `{rid}`。"]
    lines+=['',f"全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。",'','## 核实与诊断','',f"核实查询共{len(o['verification_queries'])}条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。"]
    for q in o['verification_queries']:lines+=['',f"- 核实 `{q['label']}`：`{q['source']}` 数组索引{q['index']}（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。"]
    for q in o['diagnostics']:lines+=['',f"- 诊断 `{q['label']}`：`{q['source']}` 数组索引{q['index']}（从0开始）。"]
    clocks=[c for p in o['points'] for c in p.get('clock_control',[]) if c['count']>0]
    if clocks:
        unique=list({json.dumps(c,ensure_ascii=False,sort_keys=True):c for c in clocks}.values())
        lines+=['',f"涉及运行时间的基线与单改沿用同一固定时刻：`{json.dumps(unique,ensure_ascii=False)}`；完整控制记录见复用重跑JSON。"]
    if o['main']=='不可评估':
        lines+=['','gold raw名为channel_basic_a_2/channel_demographics_a_1/video；agent/initial名为youtube_channel_basic_data/youtube_channel_demographics_data/youtube_video_data。024诊断直接比较本表读取raw的agent与initial内容，差集为0；gold结构及行数不同。按第6节，不赋错误点、五档或主因排序；同题中间层按CS另行标注。']
    if o.get('combination'):lines+=['',f"组合诊断：`{o['combination']['source']}` 索引{o['combination']['index']}，只改{o['combination']['labels']}；{sc(o['combination']['levels'])}。只用于确认组合改善，不冒充任何单点的收益。"]
    for p in o['points']:
        lines+=['',f"## 点：{p['point']}",'',f"类别：**{p['category']}**；角色：{p['role']}；把握：{p['confidence']}。",'',p['reason'],'',f"证据在场：{p['evidence_present']}；曾经理解对过：{p['previously_correct']}；系统提示是否适用：{p['system_prompt']}。"]
        if p['category']=='Intent Misreading':lines+=['','决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。']
        if p.get('P'):lines+=['',f"P：{p['P']}",'',p['evidence_presence_reason'],'',f"反证核实结果：`{json.dumps(p['verification'],ensure_ascii=False)}`。"]
        if p.get('process_note'):lines+=['',p['process_note']]
        lines+=['',f"证据：`{p['source']}`，条目 `{p['run_label']}`。",'',f"基线：{sc(p['baseline'])}。"]
        if p.get('after') is not None:
            lines+=['',f"单改后：{sc(p['after'])}。L0减量（先行后格）：{p['reduction'][0]}行/{p['reduction'][1]}格。",'', '单改替换（除此之外不变；复用024重跑记录）：','', '```json',json.dumps(p.get('edits',[]),ensure_ascii=False,indent=2),'```']
        else:lines+=['',f"只有成组诊断：排除 {p['group_diagnostic']['excluded']} 后 {sc(p['group_diagnostic']['levels'])}；没有该列独立单改收益。"]
        if p['role']=='非原因':lines+=['','本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。']
        lines+=['',f"是否说出：**第{p['disclosure']}档——{levels[p['disclosure']-1]}**。{p['disclosure_reason']}",'']
        for q in p['disclosure_citations']:lines.append(qtext(q))
        lines+=['契约／过程证据（与上段重复的引句略）：','']
        for q in p['decision_citations']:
            if q not in p['disclosure_citations']:lines.append(qtext(q))
        lines+=['',f"共同生成动作 `{p['generation_family']}`；根源决定单元 `{p['root_decision']}`。"]
    lines+=['','## 规则问题与限制','']
    if o['rule_questions']:lines += ['- '+q['point']+'：'+q['reason'] for q in o['rule_questions']]
    else:lines+=['无新增未覆盖情形；上述把握与证据限制照实保留。']
    if any(p['role']=='同类候选' for p in o['points']):lines+=['','只可定同类主因，不能报告这几列的完整单改名次；采用手册第7节同类候选例外。']
    (A/f"043_{o['object_id']}.md").write_text('\n'.join(lines)+'\n')
save(K/'formal_working.json',formal)
stats={'formal_objects':len(formal),'formal_points':sum(len(o['points']) for o in formal),'main':dict(Counter(o['main'] for o in formal)),'points':dict(Counter(p['category'] for o in formal for p in o['points'])),'roles':dict(Counter(p['role'] for o in formal for p in o['points'])),'disclosure':dict(Counter(p['disclosure'] for o in formal for p in o['points'])),'combinations':[o['object_id'] for o in formal if o['combination_only']],'root_decision_counts':shared['root_decision_counts'],'generation_counts':shared['generation_counts'],'query_counts':dict(Counter(len(o['verification_queries']) for o in formal))}
save(K/'formal_statistics.json',stats)
print(json.dumps(stats,ensure_ascii=False,indent=2))
