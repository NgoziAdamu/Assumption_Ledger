import json,re,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'records/036_checks';deliveries=json.loads((O/'delivery_sources.json').read_text());out=[]
for obj,d in deliveries.items():
 root=Path(d['sql_path']);root=next(p for p in root.parents if p.name=='dacomp-de-'+obj[:8]);files=[];comments=[]
 for p in sorted((root/'sql').rglob('*')):
  if p.is_file() and p.suffix in ['.sql','.py']:
   files.append({'path':str(p.relative_to(root)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
   for line,text in enumerate(p.read_text().splitlines(),1):
    if (p.suffix=='.sql' and re.search(r'--|/\*|\*/',text)) or (p.suffix=='.py' and text.lstrip().startswith('#')):comments.append({'path':str(p.relative_to(root)),'line':line,'text':text})
 out.append({'object':obj,'root':str(root),'final_report_file_found':bool(d['report']),'finish_events':[e['id'] for e in d['finish']],'files':files,'comments':comments,'scope':'交付SQL目录及其中代码；.tmp生成脚本是中间代码，不当成交付说明。项目原有run.py/test_single_sql.py为运行工具；轨迹中相应改动未涉及本表错误点说明。','comment_relevance':'impl-012的测试脚本注释涉及email_template脏数据，与lead首尾空白无关；impl-030的line_item注释涉及付款方式，与invoice本批错误点无关。其余SQL没有注释。'})
(O/'deliverable_inventory.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print({'objects':len(out),'sql_files':sum(sum(f['path'].endswith('.sql') for f in x['files']) for x in out),'report_files':sum(x['final_report_file_found'] for x in out),'finish_events':sum(bool(x['finish_events']) for x in out)})
