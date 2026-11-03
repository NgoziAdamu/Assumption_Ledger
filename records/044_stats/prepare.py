#!/usr/bin/env python3
"""只读既有 CSV/JSON/轨迹文字，生成044审计文件；不执行轨迹代码。"""
import csv, json, hashlib
from pathlib import Path
from collections import Counter, defaultdict
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'records/044_stats'
BATCHES = ['036','037','038','039','040','042','043']
GRADES = ['交付物里针对本处说明了','交付物里只有通用说明','过程中意识到了，交付物里没提','看到了相关信息，但没有意识到的迹象','没有迹象']
ALIASES = {'已说出的选择':'Unstated Choice','已说出的降级':'Quiet Downgrade'}
INPUTS = {}
def read(path):
    p=ROOT/path
    assert not any(x.startswith('041') for x in p.relative_to(ROOT).parts)
    b=p.read_bytes(); INPUTS[str(p.relative_to(ROOT))]=hashlib.sha256(b).hexdigest()
    return b.decode('utf-8')
def js(path): return json.loads(read(path))
def rows(path): return list(csv.DictReader(read(path).splitlines()))
def dump(name, data): (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def cat(s): return ALIASES.get(s,s)
def oid(r): return r.get('object_id') or r['task']+'_'+r['table']
def load():
    objects=[];points=[];scope=[]
    pilots={r['对象编号'] for r in rows('records/036_objects.csv') if r['benchmark']=='DAComp'}
    for b in BATCHES:
        oo=rows(f'records/{b}_objects.csv'); pp=rows(f'records/{b}_points.csv')
        selected={r['对象编号'] for r in oo}
        if b!='036':
            s=js(f'records/{b}_scope.json'); formal={oid(r) for r in s.get('formal',s.get('objects',[]))}
            assert selected-pilots==formal
            excluded=selected & pilots; assert len(excluded)==2
            selected=formal
            scope.append({'batch':b,'formal_count':len(formal),'excluded_calibration_objects':sorted(excluded),'excluded_point_rows':sum(p['对象编号'] in excluded for p in pp)})
        for i,r in enumerate(oo,2):
            if r['对象编号'] in selected: objects.append(dict(r,source=f'records/{b}_objects.csv',source_row=i))
        for i,r in enumerate(pp,2):
            if r['对象编号'] in selected: points.append(dict(r,source=f'records/{b}_points.csv',source_row=i))
    status=rows('records/013_statuses.csv')
    actual=[r['对象编号'] for r in objects if r['benchmark']=='DAComp']; expected={oid(r) for r in status if r['status']=='待标注'}
    check={'DAComp_relabelled':len(actual),'DAComp_unique':len(set(actual)),'expected':len(expected),'missing':sorted(expected-set(actual)),'extra':sorted(set(actual)-expected),'KramaBench':sum(r['benchmark']=='KramaBench' for r in objects),'batch_scope':scope}
    dump('scope_validation.json',check)
    assert len(actual)==len(set(actual))==len(expected)==283 and set(actual)==expected, '范围不符，停止'
    assert check['KramaBench']==42
    others=[r for r in status if r['status'] in ['格式差异','日期差异']]
    assert Counter(r['status'] for r in others)=={'格式差异':19,'日期差异':34}
    before=[dict(p) for p in points]
    fixes=[]
    kr=[('archeology-hard-1','只平均两个端点'),('environment-hard-16','擅限Boston Harbor'),('environment-hard-18','只取四城市淡水海滩'),('wildfire-hard-6','误缩短NOAA覆盖起点'),('biomedical-hard-8','protein与site粒度')]+[(o,'答案附带说明或额外字段') for o in ['environment-easy-2','environment-hard-15','wildfire-easy-1','wildfire-hard-4']]
    specs=[('KramaBench',o,p,'是否说出（五档）',GRADES[2],GRADES[3]) for o,p in kr]
    specs += [('DAComp','impl-006_stg_reddit_ads__campaign_report',p,'是否说出（五档）',GRADES[3],GRADES[1]) for p in ['click_through_rate','cost_per_click','cost_per_thousand_impressions']]
    specs += [('DAComp','impl-030_stg_zuora__invoice','account_source','曾经理解对过','否','是')]
    for b,o,p,k,old,new in specs:
        matched=[r for r in points if r['benchmark']==b and r['对象编号']==o and r['错误点名称']==p]
        assert len(matched)==1
        r=matched[0];cur=r[k]; applied=cur==old
        if applied:r[k]=new
        fixes.append({'benchmark':b,'object_id':o,'point':p,'field':k,'expected_old':old,'actual_old':cur,'new':new,'applied':applied,'source':r['source'],'source_row':r['source_row'],'reason':'用户任务044的13条更正；仅内存更新' if applied else '原值不一致，未改'})
    dump('corrections_applied.json',fixes)
    for a,b in zip(before,points):
        assert all(a[k]==b[k] for k in ['类别','角色','对象编号','错误点名称'])
    for r in others:
        objects.append({'benchmark':'DAComp','对象编号':oid(r),'层':r['layer'],'主要原因':'其他','并列项':'','是否只能组合修复':'否','source':'records/013_statuses.csv','source_row':status.index(r)+2,'preclassified':r['status']})
    return objects,points,status,check

def event(task,number):
    base=ROOT/f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/{task}/agent/.events/sessions'
    fs=list(base.glob(f'*/events/{number}.json'));assert len(fs)==1
    p=str(fs[0].relative_to(ROOT));d=js(p)
    return p,d.get('args',{}).get('command','')
def citation(task,number,quote):
    path,command=event(task,number);assert quote in command,(task,number,quote)
    return {'source':path,'event':number,'field':'args.command','quote':quote}
def roots(objects,points):
    orig=js('records/043_checks/shared_root_decisions.json')
    ob={r['对象编号']:r for r in objects}; ps=defaultdict(list)
    for p in points:ps[p['对象编号']].append(p)
    decisions=[];notmerged=[]
    for d in orig['decisions']:
        if d['table_count']<=1:continue
        d=dict(d);d['origin']='records/043_checks/shared_root_decisions.json'
        d['citations']=[dict(c) for c in d['citations']]
        # 原目录引句也核对留存事件，防止只依据脚本名称合并。
        for c in d['citations']:
            if c.get('event') is not None:
                _,cmd=event(d['task'],int(c['event']))
                assert c['quote'] in cmd,(d['id'],c['event'])
        decisions.append(d)
    def add(id,task,description,affected,cites):
        decisions.append({'id':id,'task':task,'description':description,'affected':affected,'citations':cites,'origin':'044只读核查'})
    def affected(ids, pred):
        return [{'object_id':o,'points':[{'point':p['错误点名称'],'role':p['角色'],'category':p['类别']} for p in ps[o] if pred(p)]} for o in ids]
    fallback=[o for o in ob if o.startswith('impl-006_') and any(p['错误点名称']=='首源投影/整表NULL替代模型（同类缺口组）' for p in ps[o])]
    fallback += ['impl-006_ad_reporting__monthly_campaign_country_report','impl-006_ad_reporting__monthly_campaign_region_report']
    add('006-event27-fallback','impl-006','同一循环以首源字段投影、无候选列填NULL，替代intermediate/marts业务模型。',affected(fallback,lambda p:p['角色'] in ['主要','并列'] and cat(p['类别'])=='Quiet Downgrade'),[citation('impl-006',27,"  source=src[0].split('.')[-1]"),citation('impl-006',27,"   else: expr=f'NULL::{c[\"data_type\"]}'"),citation('impl-006',27,"  sql='SELECT\\n'+',\\n'.join(fields)+f'\\nFROM {src[0]}'")])
    ids=['impl-007_stg_google_play__stats_installs_'+x for x in ['overview','device','app_version','os_version']]
    add('007-event23-active-device-map','impl-007','四张表重复将active_devices_last_30_days映射为active_device_installs。',affected(ids,lambda p:p['错误点名称']=='active_devices_last_30_days'),[citation('impl-007',23,"'active_devices_last_30_days':'active_device_installs'")])
    # 不把同一个文件里各自写出的占位表达式假定为同一决定。
    for task,events in [('impl-001',[21,37]),('impl-002',[23,41,43])]:
        cites=[]
        for e in events:
            _,cmd=event(task,e)
            lines=[l for l in cmd.splitlines() if any(k in l for k in ['0.0','NULL','null','Unknown'])]
            if lines:cites.append(citation(task,e,lines[0]))
        ids=[o for o in ob if o.startswith(task+'_') and any(cat(p['类别'])=='Quiet Downgrade' and p['角色'] in ['主要','并列','参与'] for p in ps[o])]
        notmerged.append({'id':task+'-placeholders','objects':ids,'events':events,'citations':cites,'reason':'已核查逐表说明、026及生成事件；是逐表SQL/常量，未找到统一占位循环或足以证明一次共同决定的原句；同脚本/同为占位不足以合并。'})
    p,cmd=event('impl-018',19);line=next(l for l in cmd.splitlines() if l.startswith('mapping='))
    ids=['impl-018_stg_salesforce__opportunity_line_item','impl-018_stg_salesforce__order']
    add('018-event19-id-map-unrepaired','impl-018','全局外键名映射到id；event57修复名单遗漏line_item与order，留下共同错误。',affected(ids,lambda p:p['错误点名称'] in ['opportunity_source','product_source','account_mapping']),[citation('impl-018',19,line),citation('impl-018',57,"# Correct field source mapping; canonical foreign keys should remain FK columns, not the row's own id."),citation('impl-018',57,"'stg_salesforce__contact':'id as account_id','stg_salesforce__user':'id as account_id,',\n'stg_salesforce__opportunity':'id as account_id,','stg_salesforce__opportunity_history':'id as account_id,',\n'stg_salesforce__contact_history':'id as account_id,'")])
    for d in decisions:
        if d['id']=='impl-030-event45-pk_alias':
            d['affected']=list(d['affected'])+affected(['impl-030_stg_zuora__invoice'],lambda p:p['错误点名称']=='account_source')
            d['cross_batch_note']='invoice采用036正式标签；039校准不重复计入。'
        d['table_count']=len(d['affected'])
    notmerged.append({'id':'007-apple-subscription-mapping','objects':['impl-007_stg_apple_store__sales_subscription_event_summary','impl-007_stg_apple_store__sales_subscription_summary'],'citations':[citation('impl-007',23,"'subscriber_id':'subscriber_id_vendor'"),citation('impl-007',39,'TRY_CAST(subscribers AS BIGINT) AS active_subscriptions')],'reason':'不同目标与来源字段，summary还在event39独立修改；不能由同组意识推断同一个字段决定。'})
    # 根源单位是保守对象折叠：必须覆盖对象全部主要/并列/组合/同类候选点。
    merged=[]; used=set()
    for d in decisions:
        eligible=[]
        for a in d['affected']:
            o=a['object_id']; have={x['point'] for x in a['points']}; primary={p['错误点名称'] for p in ps[o] if p['角色'] in ['主要','并列','组合项','同类候选']}
            if primary and primary<=have:eligible.append(o)
            else:notmerged.append({'id':d['id'],'objects':[o],'reason':'根源只覆盖部分主因/并列项，或仅参与/非原因；整对象合并会吞掉其他独立原因。','uncovered_primary_points':sorted(primary-have)})
        eligible=sorted(set(eligible)-used)
        if len(eligible)>=2:
            used.update(eligible); merged.append({'root_id':d['id'],'task':d['task'],'objects':eligible})
        else:notmerged.append({'id':d['id'],'objects':eligible,'reason':'满足全部主因覆盖条件的对象不足两张，无可折叠单位。'})
    for d in decisions:
        for a in d['affected']:
            o=a['object_id'];a['authoritative_object_source']=ob[o]['source']
            a['authoritative_points']=[{'source':p['source'],'source_row':p['source_row'],'point':p['错误点名称'],'role':p['角色'],'category':p['类别']} for p in ps[o] if p['错误点名称'] in {x['point'] for x in a['points']}]
    # 记录核查范围：不是声称已枚举全部可能的根源决定。
    for b in BATCHES:
        for p in (ROOT/'notes').glob(b+'_*.md'):read(str(p.relative_to(ROOT)))
    read('records/026_Claude全量标注检查台账.md');read('docs/标注手册_v3.2.md')
    result={'rule':'只合并有共同具体规则证据且该规则覆盖对象全部主因点的对象；混合主因保留类别集合，不重新判类；跨根源的对象保守独立；未列为根源的所有对象独立。','decisions':decisions,'merged_object_groups':merged,'not_merged':notmerged,'singleton_objects':[o for o in sorted(ob) if o not in used],'coverage_note':'核查指定五组及043已列多对象规则；其余无充分证据者保留逐对象单位，不宣称完整因果去重。','review_sources':['records/026_Claude全量标注检查台账.md','records/037_annotations/','records/038_annotations/','records/042_annotations/','records/043_checks/shared_root_decisions.json']}
    dump('shared_root_catalog.json',result);return result

def delivery():
    d=js('records/036_checks/delivery_sources.json'); out=[]
    for i in range(1,31):
        task=f'impl-{i:03}'; matches=[(k,v) for k,v in d.items() if k.startswith(task+'_')];assert len(matches)==1
        k,v=matches[0];fin=v.get('finish',[])
        out.append({'task':task,'finish_count':len(fin),'finish_events':[x.get('id',x.get('event')) for x in fin],'finish_paths':[x['path'] for x in fin],'retained_report_path':v.get('report_path'),'new_completion_claim':i!=7,'old_completion_claim':i!=11,'source':'records/036_checks/delivery_sources.json'})
        assert bool(fin)==(i!=7)
        for f in fin:
            ev=js(f['path']);assert ev.get('action')=='finish'
    for b in BATCHES[1:]:js(f'records/{b}_checks/'+('formal_delivery_sources.json' if b=='043' else 'delivery_sources.json'))
    dump('completion_claims.json',out);return out
if __name__=='__main__':
    oo,pp,ss,check=load();roots(oo,pp);delivery();dump('input_hashes.json',INPUTS)
    print('范围通过；更正',sum(x['applied'] for x in json.loads((OUT/'corrections_applied.json').read_text())),'/13')
