"""只读重放026存档的旧统计脚本，取得158张成员用于差异说明。"""
import contextlib,io,runpy,sys,json
import prepare as P

def load_old():
    path='scripts/compute_dacomp_preliminary_results.py';P.read(path)
    for b in ['018','019','020','021','022','023','024']:P.read(f'records/{b}_annotations/{b}_summary.csv')
    P.read('notes/026_2026-10-30_存档Claude标注检查材料.md')
    oldargv=sys.argv[:];buf=io.StringIO()
    try:
        sys.argv=[str(P.ROOT/path),str(P.ROOT)]
        with contextlib.redirect_stdout(buf):d=runpy.run_path(str(P.ROOT/path))
    finally:sys.argv=oldargv
    (P.OUT/'historical_026_stdout.txt').write_text(buf.getvalue())
    own={t['task']+'_'+t['table'] for t in d['own']};said={t['task']+'_'+t['table'] for t in d['spec_all']};silent=own-said
    assert len(own)==183 and len(silent)==158
    table={t['task']+'_'+t['table']:t for t in d['T']}
    P.dump('historical_026_members.json',{'source_script':path,'own_objects':sorted(own),'disclosed_objects':sorted(said),'silent_objects':sorted(silent),'bootstrap_note':'026原始bootstrap用于其大类比例；044另用统一的20261103/10000规则计算158张参照的区间。'})
    return own,silent,table
