"""阶段一完整性检查。阶段一通过不表示50+2最终交付完成。"""
from pathlib import Path
import csv, hashlib, json, subprocess
R=Path('records'); C=R/'043_checks'
def load(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csvrows(p):
    with Path(p).open() as f:return list(csv.DictReader(f))
scope=load(R/'043_scope.json'); work=load(C/'calibration_working.json'); seal=load(R/'043_calibration_blind_sealed.json')
objects=csvrows(R/'043_objects.csv');points=csvrows(R/'043_points.csv');checks=[]
def check(name,ok,detail=None):checks.append({'name':name,'passed':bool(ok),'detail':detail})
with (R/'036_objects.csv').open() as f:pilot={r['对象编号'] for r in csv.DictReader(f)}
expected={r['task']+'_'+r['table'] for r in csvrows(R/'013_statuses.csv') if r['status']=='待标注' and 'impl-022'<=r['task']<='impl-030' and r['task']+'_'+r['table'] not in pilot}
check('范围按完整对象编号为50张',len(expected)==50 and expected=={r['object_id'] for r in scope['formal']})
check('校准范围2张准确',{r['对象编号'] for r in objects}==set(scope['calibration']) and len(objects)==2)
check('正式表尚未计入校准CSV',not ({r['对象编号'] for r in objects}&expected))
check('35个点键唯一',len(points)==35 and len({(r['对象编号'],r['错误点名称']) for r in points})==35)
levels=['交付物里针对本处说明了','交付物里只有通用说明','过程中意识到了，交付物里没提','看到了相关信息，但没有意识到的迹象','没有迹象']
check('五档取值合法',all(p['是否说出（五档）'] in levels for p in points))
check('已说出类别与第1档一致',all((p['类别'] not in ['已说出的选择','已说出的降级'] or p['是否说出（五档）']==levels[0]) and (p['是否说出（五档）']!=levels[0] or p['类别'] not in ['Unstated Choice','Quiet Downgrade']) for p in points))
check('探索字段合法',all(p['证据在场'] in ['是','否'] and p['曾经理解对过'] in ['是','否'] if p['类别'] in ['Data Misconception','Intent Misreading'] else p['证据在场']=='不适用' and p['曾经理解对过']=='不适用' for p in points))
old24={r['task']+'_'+r['table']:r['category'] for r in load(R/'024_decisions.json')}
check('024旧主要原因原样保存',all(r['024旧标签']==old24[r['对象编号']] for r in objects+points))
for typ in ['objects','points']:
    with (R/f'042_{typ}.csv').open() as f:h42=next(csv.reader(f))
    with (R/f'043_{typ}.csv').open() as f:h43=next(csv.reader(f))
    check(typ+'表头与042一致且最后为024旧标签',h42[:-1]==h43[:-1] and h43[-1]=='024旧标签')
check('封存件hash不变',sha(R/'043_calibration_blind_sealed.json')==load(C/'calibration_seal_hash.json')['sha256'])
check('校准前缀保存一致',all((C/f'phase1_{typ}_prefix.csv').read_bytes()==(R/f'043_{typ}.csv').read_bytes() for typ in ['objects','points']))
check('核实查询预算不超过5',all(q['total']<=5 for q in seal['query_budget'].values()))
check('新查询只有1条且只读',len(load(C/'calibration_queries.json'))==1 and all(q['read_only'] for q in load(C/'calibration_queries.json')))
check('校准逐表说明2份',len(list((R/'043_annotations').glob('*.md')))==2)
check('50张证据目录和raw引用齐全',len(load(C/'evidence_catalog.json'))==50 and all(Path(x['package']).exists() and Path(x['raw_review_source']).exists() for x in load(C/'evidence_catalog.json')))
def quotes(x):
    if isinstance(x,dict):
        if {'source','event','field','quote'} <= x.keys():yield x
        else:
            for v in x.values():yield from quotes(v)
    elif isinstance(x,list):
        for v in x:yield from quotes(v)
audit=[];cache={}
for f in [R/'043_calibration_blind_sealed.json',C/'calibration_working.json',C/'disclosure_audit.json',C/'026_review_preparation.json',C/'shared_root_decisions.json']:
    for q in quotes(load(f)):
        if q['source'] not in cache:cache[q['source']]={e['id']:e for pair in load(q['source'])['history'] for e in pair if 'id' in e}
        s=cache[q['source']][q['event']]
        for k in q['field'].split('.'):s=s[k]
        audit.append({'record':str(f),**q,'matched':q['quote'] in s})
check('全部引句回查原文成功',all(q['matched'] for q in audit),len(audit))
(C/'quote_checks.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
hashes={**load(C/'input_hashes_before.json')['sha256'],**load(C/'input_hashes_supplement.json')['sha256']}
changed=[p for p,h in hashes.items() if not Path(p).exists() or sha(p)!=h]
check('018～040及042记录和两版手册hash不变',not changed,{'checked':len(hashes),'changed':changed})
git041=subprocess.check_output(['git','ls-files','-s','notes/041*','records/041*'],text=True)
check('041索引对象编号不变且工作区未改',git041==load(C/'input_hashes_before.json')['041_git_index_only'] and subprocess.run(['git','diff','--quiet','HEAD','--','notes/041*','records/041*']).returncode==0,'未读取041正文；使用git对象编号及工作区差异检查。')
check('校准定稿文件hash保持交接值',all(sha(p)==h for p,h in load(C/'phase1_handoff.json')['calibration_file_hashes'].items()))
diff=subprocess.run(['git','diff','HEAD','--check'],capture_output=True,text=True)
check('git diff --check通过',diff.returncode==0,diff.stdout+diff.stderr)
out={'status':'phase1_complete_phase2_pending' if all(c['passed'] for c in checks) else 'failed','task_complete':False,'formal_expected':50,'formal_completed':0,'calibration_completed':2,'point_count':len(points),'checks':checks,'final_52_object_check':'pending：当前CSV只有校准2张，不声称已通过52张终检。'}
(C/'validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(out['status'],sum(c['passed'] for c in checks),'/',len(checks),'quotes',len(audit))
assert all(c['passed'] for c in checks),[c for c in checks if not c['passed']]
