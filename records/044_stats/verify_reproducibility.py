#!/usr/bin/env python3
"""完整入口连续执行两次，比对全部输出字节；不读其他任务内容。"""
import subprocess,sys,hashlib,json,os
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def snapshot():
    paths=[p for p in OUT.iterdir() if p.is_file() and p.name!='reproducibility.json']+[ROOT/'notes/044_2026-11-03_重标总统计.md']
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
def once():
    result=subprocess.run([sys.executable,'-B',str(OUT/'run.py')],cwd=ROOT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True)
    if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    return snapshot()
a=once();b=once();diff=[p for p in a if a[p]!=b[p]];assert not diff,diff
(OUT/'reproducibility.json').write_text(json.dumps({'command':'python -B records/044_stats/verify_reproducibility.py','runs':2,'compared_files':len(a),'all_byte_identical':not diff,'differences':diff,'sha256':b},ensure_ascii=False,indent=2)+'\n')
print(f'完整入口连续执行两次：{len(a)}个文件字节一致。')
