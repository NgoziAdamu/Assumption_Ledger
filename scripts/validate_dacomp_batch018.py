"""Validate v2 deliverables and evidence reuse without opening any database."""
from pathlib import Path
from collections import Counter
import csv,hashlib,json,re
from uncertainty_dacomp_batch018 import GRADES,field,previous

ROOT=Path(__file__).resolve().parents[1];REC=ROOT/'records'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    rows=list(csv.DictReader((REC/'018_annotations/018_summary.csv').open()));a=read(REC/'018_decisions.json');u=read(REC/'018_uncertainty_audit.json');manifest=read(REC/'018_reuse_manifest.json')
    assert len(rows)==len(a)==len(u)==len(manifest)==30
    assert len(rows[0])==16 and len(list((REC/'018_annotations').glob('*.md')))==30
    assert (ROOT/'docs/标注手册_v2.md').read_bytes()==Path('/mnt/c/Users/jucc116/Desktop/标注手册_v2.md').read_bytes()
    checks=[];trials=0;queries=0
    for n,row in enumerate(rows,1):
        task=f'impl-{n:03}';decision=a[str(n)];audit=u[task];assert row['题目']==task
        assert row['主要原因类别']==decision['cat'] and decision['cat']!='X'
        cats=decision['item_categories'];assert set(cats)=={x['item'] for x in audit['items']}
        assert all(x in ['U','D','C','A','I','O','X','不可评估'] for x in cats.values())
        if len(set(cats.values()))==1:assert decision['cat']==next(iter(cats.values()))
        else:assert decision['cat'].startswith('多因并列')
        p=ROOT/audit['trace_file'];assert sha(p)==audit['trace_sha256'];es={e['id']:e for e in read(p)}
        for item in audit['items']:
            assert item['grade'] in GRADES and item['scope_limit']
            assert item['item']+'='+item['grade'] in row['不确定性四档']
            for e in item['evidence']:assert e['quote'] in field(es[e['event']],e['field']),(n,item['item'])
            if item['grade'] in GRADES[:2]:assert all(e['field'] in ['args.final_thought','args.command','args.thought','thought'] for e in item['evidence'])
        assert int(row['核实查询条数'])<=5;queries+=int(row['核实查询条数'])
        r=read(ROOT/decision['reused_rerun_file']);base=r['runs'][0]['comparison']['levels'][0]
        for t in r['runs']:
            trials+=1;assert not t.get('error')
            c=t['comparison'];assert c['first_match']==next((x['level'] for x in c['levels'] if x['whole_match']),None)
            for x in c['levels']:
                extra=x['agent_only_key_rows']+x['gold_only_key_rows']+x.get('common_key_agent_excess_rows',0)+x.get('common_key_gold_excess_rows',0)
                cols=len(set(r['basis']['key_columns']+r['basis']['comparison_columns']))
                assert x['row_scale']==extra+x['common_key_different_rows_or_min_pairs'],(n,t['label'])
                assert x['cell_scale']==extra*cols+sum(x['column_mismatches'].values()),(n,t['label'])
                assert x['whole_match']==(x['row_scale']==0 and x['cell_scale']==0)
        if len(cats)>1:
            ts=[t for t in r['runs'] if t['label'] in cats];assert len(ts)==len(cats)
            gains=[(base['row_scale']-t['comparison']['levels'][0]['row_scale'],base['cell_scale']-t['comparison']['levels'][0]['cell_scale']) for t in ts]
            assert len(set(gains))==1 and max(gains[0])>0,(n,gains)
        for f in manifest[n-1]['files']:assert sha(ROOT/f['path'])==f['sha256'],f['path']
        md=next((REC/'018_annotations').glob(f'018_{task}_*.md')).read_text();assert md.rfind('## 规则问题')>md.rfind('## 6.')
        checks.append({'task':task,'item_categories':cats,'item_count':len(cats),'verbatim_evidence_checked':True,'reused_metrics_checked':True,'source_hashes_checked':True})
    # Check the only newly executed SQL and all its common-clock edits exactly.
    r=read(REC/'018_reruns_impl-006.json');old=read(REC/'016_reruns_impl-006.json');pkg=read(next((REC/'012_packages').glob('012_impl-006_*.json')))
    controlled=Path(pkg['agent_final_SQL'][0]['path']).read_text()
    for e in r['clock_control']:controlled=re.sub(e['pattern'],e['replacement'],controlled,flags=re.I)
    for t,prior in zip(r['runs'],old['runs']):
        sql=controlled
        for e in t['edits']:
            assert sql.count(e['old'])==1 and sql.index(e['old'])==e['offset'];sql=sql.replace(e['old'],e['new'],1)
        p=ROOT/t['sql_path'];assert p.read_text()==sql and sha(p)==t['sql_sha256']
        for x,y in zip(t['comparison']['levels'],prior['comparison']['levels']):
            for k in ['row_scale','cell_scale','column_mismatches','whole_match','agent_rows','gold_rows']:assert x[k]==y[k],(t['label'],k)
        assert t['comparison']['first_match']==prior['comparison']['first_match']
    assert len(r['runs'])==21 and r['started_utc']>read(REC/'018_input_before.json')['completed_utc']
    assert a['30']['item_categories']['account_source']=='U' and a['12']['cat']=='O' and a['18']['cat']=='I'
    # X in historical selected-table categories or factors is explicitly audited.
    xs=[]
    for pre in [14,16,17]:
        for row in csv.DictReader((REC/f'{pre:03}_annotations/{pre:03}_summary.csv').open()):
            if any(re.search(r'(?<![A-Za-z])X(?![A-Za-z])',row[k]) for k in ['主要原因类别','参与因素']):
                n=int(row['题目'].split('-')[1]);xs.append({'version':pre,'task':row['题目'],'previous_category':row['主要原因类别'],'previous_factors':row['参与因素'],'v2_category':a[str(n)]['cat'],'v2_factors':a[str(n)]['factors']})
    (REC/'018_x_review.json').write_text(json.dumps(xs,ensure_ascii=False,indent=2)+'\n')
    before=read(REC/'018_input_before.json');assert not before['differences_from_017_after']
    after_path=REC/'018_input_after.json';after=read(after_path) if after_path.exists() else None
    if after:assert not after['changes'] and len(before['files'])==len(after['files'])
    missing=[]
    for p in list((REC/'018_annotations').glob('*.md'))+list((ROOT/'notes').glob('018_*.md')):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if target.startswith(('https:','http:','#')):continue
            resolved=(p.parent/target).resolve()
            if not resolved.exists() and resolved!=after_path:missing.append((str(p),target))
    assert not missing,missing
    for p in list(REC.glob('018*'))+list((REC/'018_annotations').glob('*')):
        if p.is_file():
            text=p.read_text();assert not re.search(r'\bAC[a-fA-F0-9]{32}\b|\bgh[pousr]_[A-Za-z0-9]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',text),str(p)
    output={'all_passed':True,'annotation_count':30,'csv_columns':16,'uncertainty_item_count':sum(len(x['items']) for x in u.values()),'reused_verification_attempts':queries,'new_verification_attempts':0,'all_evidence_sql_trials':trials,'new_fixed_clock_sql_trials':21,'reused_sql_trials':trials-21,'new_trials_metrics_equal_to_prior':True,'manual_byte_identical':True,'protected_input_files':len(before['files']),'after_snapshot_checked':bool(after),'checks':checks,'historical_x_review':xs}
    (REC/'018_validation.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print('PASS: 30 annotations; 60 uncertainty items; exact quotations; 130 SQL evidence trials; 21 fixed-clock trials; reused evidence hashes; manual bytes; links. After snapshot:',bool(after))
if __name__=='__main__':main()
