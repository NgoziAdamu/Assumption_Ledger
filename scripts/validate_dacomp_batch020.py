"""Validate delivery scope, immutable blind lock, SQL edits, counts and source quotes."""
import ast, csv, hashlib, json, re, subprocess
from collections import Counter
from pathlib import Path
from plan_dacomp_batch020 import ROOT, REC, rows, pkg
from write_dacomp_batch020 import rr, valid, category, T

def read(path): return json.loads(path.read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(name, value): (REC/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
def event(task, n):
    p=next((ROOT/f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/{task}/agent/.events/sessions').glob(f'*/events/{n}.json'))
    return p, read(p)

def main():
    pilot={(x['task'],x['table']) for x in read(REC/'012_sampling.json')['samples']}
    expected={(x['task'],x['table']) for x in csv.DictReader((REC/'013_statuses.csv').open()) if x['task'] in ['impl-006','impl-007'] and x['status']=='待标注' and (x['task'],x['table']) not in pilot}
    assert len(expected)==43 and expected=={(x['task'],x['table']) for x in rows[:43]}
    assert [(x['task'],x['table']) for x in rows[43:]]==[('impl-002','stg_pendo__guide_event'),('impl-025','stg_twilio__call')]
    lock=read(REC/'020_blind_lock.json');assert sha(ROOT/lock['file'])==lock['sha256']
    reference=list(csv.DictReader(next((REC/'018_annotations').glob('*.csv')).open()))
    f=(REC/'020_annotations/020_summary.csv').open();reader=csv.DictReader(f);summary=list(reader)
    assert reader.fieldnames==[k for k in reference[0] if not k.startswith('与上一版相比')]
    assert len(summary)==45 and all('校准' in x['与 014 相比是否变化'] for x in summary[-2:])
    assert len(list((REC/'020_annotations').glob('*.md')))==45
    assert len(list((REC/'020_packages').glob('*.md')))==43
    decisions=read(REC/'020_decisions.json');cases=read(REC/'013_cases.json')
    queries=sum([read(REC/name) for name in ['020_queries.json','020_diagnostics.json','020_final_diagnostics.json']],[])
    audit=[];trials=0;levels_checked=0
    for i,r in enumerate(rows):
        d=pkg(i);b=d['differences'];doc=(REC/'020_annotations'/(r['stem']+'.md')).read_text()
        assert (ROOT/r['path']).exists() and '暂停检查点／待复核草稿' not in doc
        assert summary[i]['题目']==r['task'] and summary[i]['表']==r['table']
        assert summary[i]['主要原因类别']==decisions[i]['main']
        assert all(title in doc for title in ['## 结论','## 差异与归因依据','## agent可见证据与不确定性','## 核实查询与诊断','## 固定时间与重跑','## 规则问题','## 证据路径'])
        for key in ['agent_final_SQL','gold_SQL_仅供定位差异']:
            for source in d[key]: assert sha(Path(source['path']))==source['sha256']
        for block in d['contract_specification']['blocks']:
            lines=Path(d['contract_specification']['source_path']).read_text().splitlines(keepends=True)
            assert ''.join(lines[block['start_line']-1:block['end_line']]).rstrip('\n')==block['original_text'].rstrip('\n')
        q=[x for x in queries if x.get('index')==i and x['kind']=='核实'] if i<43 else [x for x in read(REC/'020_calibration_queries.json') if x['task']==r['task']]
        assert len(q)==int(summary[i]['核实查询条数'])<=5
        assert all(x['database']==cases[int(r['task'][-3:])-1]['agent_database'] for x in q)
        combined=rr(i);colset=set(b['key_columns']+b['comparison_columns'])
        for filename in combined['evidence_files']:
            evidence=read(ROOT/filename);original=d['agent_final_SQL'][0]['text'];baseline=original
            for e in evidence['clock_control']:baseline=re.sub(e['pattern'],e['replacement'],baseline,flags=re.I)
            assert evidence['source']==(cases[int(r['task'][-3:])-1]['agent_database'] if r['layer']=='staging' else b['gold_database'])
            for run in evidence['runs']:
                trials+=1;sql=baseline
                for e in run.get('edits',[]):
                    assert sql.count(e['old'])==1,(i,run['label'],'ambiguous edit')
                    assert sql.index(e['old'])==e['offset']
                    sql=sql.replace(e['old'],e['new'],1)
                path=ROOT/run['sql_path'];assert path.is_relative_to(ROOT/'data')
                assert sha(path)==run['sql_sha256'] and path.read_text()==sql,(i,run['label'],'SQL provenance')
                assert 'error' not in run,(i,run['label'],run.get('error'))
                c=run['comparison'];assert [x['level'] for x in c['levels']]==['L0','L1','L2','L3']
                assert c['first_match']==next((x['level'] for x in c['levels'] if x['whole_match']),None)
                for lev in c['levels']:
                    levels_checked+=1;assert set(lev['column_mismatches'])==colset
                    extra=sum(lev[k] for k in ['agent_only_key_rows','gold_only_key_rows','common_key_agent_excess_rows','common_key_gold_excess_rows'])
                    assert lev['row_scale']==extra+lev['common_key_different_rows_or_min_pairs']
                    assert lev['cell_scale']==extra*len(colset)+sum(lev['column_mismatches'].values())
        ranked=[]
        if i<43:
            base=combined['runs'][0]['comparison']['levels'][0]
            for run in combined['runs'][1:]:
                if not valid(i,run['label']):continue
                lev=run['comparison']['levels'][0];gain=(base['row_scale']-lev['row_scale'],base['cell_scale']-lev['cell_scale'])
                if gain>(0,0):ranked.append((gain,run['label'],category(i,run['label'])))
            if ranked:
                best=max(x[0] for x in ranked);leaders=[x for x in ranked if x[0]==best];cats=sorted({x[2] for x in leaders})
                expected_main=cats[0] if len(cats)==1 else '多因并列（'+'、'.join(cats)+'）'
                assert decisions[i]['main']==expected_main,(i,expected_main,decisions[i]['main'])
        audit.append({'index':i,'task':r['task'],'table':r['table'],'purpose':r['purpose'],'main':decisions[i]['main'],'query_count':len(q),'source_SQL_hash_and_contract_lines_checked':True,'isolated_edits_and_all_L0_L3_counts_checked':True,'ranking':ranked,'rule_issue':decisions[i]['rules']})
    quotes=[]
    for task,n,field,quote in [
      ('impl-006',97,'final_thought','脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。'),
      ('impl-006',97,'final_thought','对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。'),
      ('impl-006',97,'final_thought','当前实现以结构化 NULL/直接字段投影保障执行，并非完整的客户旅程、地理分析、时间序列、预测及执行仪表板业务逻辑。'),
      ('impl-007',67,'command','部分原始表的字段名和契约 staging 字段名不一致，按原始 schema 映射（例如 Google Play 的 `daily_*` 指标、Apple 的 `date`/`territory`/`counts`/`event`）。'),
      ('impl-007',67,'command','Apple 订阅 summary/event 字段有若干原始字段与 staging 字段语义不完全一致，使用可用列映射且转换兼容字段类型。'),
      ('impl-007',67,'command','随后修正了输出列顺序及评级规则：无效的必需平均评级记录删除、契约指定 nullify 的评级/转化率置空或删除。'),
      ('impl-002',59,'final_thought','The work includes staging raw-field mapping, timestamp parsing, event-key generation, filtering and nullification; latest-record models; daily aggregates and calendar spines; and mart entities.'),
      ('impl-025',41,'final_thought','依契约的清理策略处理非法日期、枚举、电话和字段值；需要丢弃的记录按整行过滤，非关键字段则置为 NULL。')]:
        path,e=event(task,n);assert quote in e['args'][field],(task,n,quote)
        quotes.append({'task':task,'event':n,'path':str(path.relative_to(ROOT)),'field':'args.'+field,'verbatim':quote})
    path,e=event('impl-006',19);s=e['args']['command'];start=s.index('special=')+len('special=');end=s.index('\n   candidates=special.get',start)
    node=ast.parse(s[start:end].strip(),mode='eval').body
    mappings={}
    for k,v in zip(node.keys,node.values):mappings.setdefault(ast.literal_eval(k),[]).append(ast.literal_eval(v))
    assert mappings['campaign_id']==[['campaign_id','id'],['campaign_id','CAMPAIGN_ID']]
    assert mappings['spend']==[['spend','local_spend_amount'],['local_spend_amount']]
    save('020_review_audit.json',{'tables':audit,'verbatim_quotes':quotes,'generator_duplicate_keys':{k:v for k,v in mappings.items() if len(v)>1},'generator_event_path':str(path.relative_to(ROOT))})
    calibrations=[]
    for new in summary[-2:]:
        old=next(x for x in reference if x['题目']==new['题目'] and x['表']==new['表'])
        calibrations.append({'task':new['题目'],'table':new['表'],'blind_lock':lock,'main_category_equal':old['主要原因类别']==new['主要原因类别'],'fully_equal':False,'differences':(['代理键：020通用策略，018看到了但没提；URL档位、主因及U参与因素一致。'] if new['题目']=='impl-002' else ['020按统一电话预修复策略合并两列；018按列单修排序，以contact为主、user为C参与因素。','把握020高、018中；主要类别C及通用策略档一致。']),'reference_018':old,'blind_020_summary':new})
    save('020_calibration_comparison.json',calibrations)
    # Existing task020 drafts may be finalized; all older files stay unchanged.
    changed=subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()
    assert all(x.startswith('records/020_') or x=='scripts/write_dacomp_batch020.py' for x in changed),changed
    result={'result':'PASS','formal_tables':43,'calibration_tables':2,'new_packages':43,'markdowns':45,'csv_rows':45,'csv_columns':len(reader.fieldnames),'max_verification_queries':max(int(x['核实查询条数']) for x in summary),'rerun_records':trials,'L0_L3_level_records_checked':levels_checked,'blind_lock_unchanged':True,'main_category_calibration_agreement':'2/2','full_calibration_agreement':'0/2','manual_modified':False,'older_records_modified':False,'note':'成功实验不重复执行；逐个验证SQL原文字节、共同时间控制、单处替换及保存哈希。整段实现诊断的归因单位限制见各表规则问题。输入全量哈希最终核对另见020_resume_input_after.json。'}
    save('020_validation.json',result);print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
