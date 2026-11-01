"""只读取封存原件；生成解盲对比，不得覆写盲标。"""
import csv,json,hashlib,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[2]
def read(p):return json.loads((R/p).read_text())
seal=read('records/037_checks/calibration_seal.json');blob=(R/seal['sealed_path']).read_bytes();assert hashlib.sha256(blob).hexdigest()==seal['sha256']
b=json.loads(blob);ids={o['对象编号'] for o in b['objects']}
old={r['对象编号']:r for r in csv.DictReader((R/'records/036_objects.csv').open()) if r['对象编号'] in ids}
pold={r['对象编号']:r for r in csv.DictReader((R/'records/036_points.csv').open()) if r['对象编号'] in ids}
audit={r['对象编号']:r for r in read('records/036_checks/disclosure_audit.json') if r['对象编号'] in ids}
rows=[]
for o in b['objects']:
 id=o['对象编号'];p=o['points'][0];k='impl-021' in id
 rows.append({'对象编号':id,'blind_main':o['主要原因'],'036_main':old[id]['主要原因'],'main_equal':o['主要原因']==old[id]['主要原因'],'blind_grade':p['disclosure_grade'],'036_grade':audit[id]['grade'],'grade_equal':p['disclosure_grade']==audit[id]['grade'],'blind_confidence':o['把握'],'036_confidence':old[id]['把握'],'036_object_verbatim':old[id],'036_point_verbatim':pold[id],'036_disclosure_verbatim':audit[id],'post_comparison':{'main':'Intent Misreading' if k else 'Data Misconception','grade':2 if k else 4,'confidence':'中' if k else '高','decision':'解盲后修订（不修改盲标、不计为盲标一致）' if k else '维持盲标主因与档位','reason':'盲标能构造连接不扩行的 P，但遗漏第5节“规格规定做法”边界的优先性：本契约直接定义 missing_day_count 为没有事件的 spine 日期数，并强调同日多事件不得改变计数。按定义实现即可改对，最终采用 Intent Misreading。报告“事件重复保留且照常计数”是泛指事件处理的策略，可记第2档；它没有点名 missing_day_count，不能升第1档。盲标把该句仅限于 attribution 的读法过窄。' if k else '明确缺失项目的材料和 agent staging 反例支持 Data；第4档一致。把握差异保留：本次主因采用高。','evidence_presence':'是','previously_understood':'否'},'point_coverage_difference':'037 另外列出 projects_sections 同名内并列顺序（其他，参与）；036 points.csv 未单列此点。037 新诊断确认 79/79 字符串差异仅同名组内次序。该点不改变主要原因。' if not k else '两种单改修复同一个错误点，不重复计点。','rule_question':'Data/Intent 都可描述其机制；本次解盲后按规格规定指标的边界选 Intent。第2档通用说明覆盖范围也有宽窄读法；按共享事件重复处理的宽读记2，并明确非本指标具体披露。' if k else 'project_source 的类型/排序副作用不拆成独立重复点；其他顺序因素仍单列。'})
out={'sealed_path':seal['sealed_path'],'sealed_sha256_before_comparison':seal['sha256'],'compared_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'comparison_sources':['records/036_objects.csv','records/036_points.csv','records/036_checks/disclosure_audit.json','records/034_annotations/dacomp_impl-021_int_klaviyo__person_metrics.md'],'main_agreement':{'equal':1,'total':2},'grade_agreement_on_shared_primary_points':{'equal':1,'total':2},'comparisons':rows,'sealed_sha256_after_comparison':hashlib.sha256((R/seal['sealed_path']).read_bytes()).hexdigest(),'policy':'盲标一致率只按封存原件；解盲后修订不得冒充盲标一致。037 表格若使用解盲后结果，逐表明确注明。'}
assert out['sealed_sha256_after_comparison']==seal['sha256']
(R/'records/037_calibration_comparison.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('comparison saved; blind main/grade agreement: 1/2, 1/2')
