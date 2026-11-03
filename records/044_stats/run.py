#!/usr/bin/env python3
"""完整入口：只读旧输入，全部输出限定于044。"""
import contextlib,io,hashlib,json
import prepare as P
import stats,report,validate
buf=io.StringIO()
with contextlib.redirect_stdout(buf):stats.main()
(P.OUT/'run_summary.json').write_text(buf.getvalue())
report.main()
v=json.loads((P.OUT/'validation.json').read_text())
v['all_input_hashes_unchanged']=all(hashlib.sha256((P.ROOT/p).read_bytes()).hexdigest()==h for p,h in P.INPUTS.items())
assert v['all_input_hashes_unchanged']
v['report']='notes/044_2026-11-03_重标总统计.md'
v['manual_review_primary_count']=6
v['outputs']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(P.OUT.iterdir()) if p.is_file() and p.name not in ['validation.json','reproducibility.json'] and p.suffix in ['.csv','.json','.txt']}
P.dump('validation.json',v)
validate.run()
print('通过：范围、13条更正、所有比例成员与95%范围、原输入hash。')
