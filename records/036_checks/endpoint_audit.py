"""Audit reused endpoint evidence; no execution of034 scripts and no writes to034."""
import json,re,hashlib,csv
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'records/036_checks'
def load(n):return json.loads((R/'records/034_checks'/n).read_text())
def blocks(id):return dict(re.findall(r'<!-- original:(.*?) chars:\d+ -->\n```[^\n]*\n(.*?)\n```',(R/f'records/028_kramabench_packages/{id}.md').read_text(),re.S))
# Includes the constant-final diagnostics plus calculations whose original final was an expression.
checks=[
('archeology-hard-1','archeology-hard-1_interval_mean.json','step8打印的vals.mean→最终常量；034 suffix重算mean并保留round4，符合引用规则。差230.3411→99.9825。类别不变。'),
('archeology-hard-7','archeology-hard-7_euclidean.json','原最终调用依赖改后的计数，292→274，符合终点规则。只有交付档位导致类别改变。'),
('archeology-hard-9','archeology-hard-9_highest_rank_diagnostic.json','step6改选rank，step7重算相关系数，suffix与step9最终round6相同；0.015648是完整计算结果。题面last/子任务highest冲突仍保留其他。'),
('astronomy-easy-6','astronomy-easy-6_endpoint_diagnostic.json','034 endpoint suffix同时改估计器、符号和round4，不能当成原单改终点。036已保留原round6、分开估计器与符号重算；组合剩0.000056。主要/参与/只能组合修复按新规模修正。'),
('astronomy-hard-8','astronomy-hard-8_chrono70_retry.json','034重算的是另一候选输出（时间顺序70/30），不是原最终seed42随机80/20的单处源码修改；只能作候选方案诊断。036不依它排序。第7节同类候选规则仍可定Choice类别。'),
('environment-easy-3','environment-easy-3_all_beaches.json','034复用agent自己step7的全量海滩分组计算，268取代后续Boston限定的3，终点是计数而非中间行数；范围项结论成立。'),
('environment-hard-16','environment-hard-16_all_beaches.json','原step6计算safe_count、step8常量0引用该计数；034扩大海滩范围后沿相同无违规判据得到74。名称与community+name诊断74/75的残差已保留，不追加身份类别。'),
('environment-hard-18','environment-hard-18_combination.json','原最终False引用step3–5的水质/雨量趋势。034重算后以逐年方向是否全相同作布尔解释，baseline/范围单改/大小写单改/组合=False/False/False/True。保留034多因并列和只能组合修复，但这一步布尔化无显式原代码，属解释性诊断，不声称原字节级单改；列规则问题。'),
('legal-hard-17','legal-hard-17_printed_share_success.json','step5 estimate随份额重算且final_answer(estimate)，32542为真实终点；类别变化只来自最终没说明份额选择。'),
('legal-hard-18','legal-hard-18_retry.json','原step6的259314*over40/known按千位round后由step7常量126000引用。034替换基数为1070447*.1754后保留over40/known与千位round，得到91000。符合引用规则，类别不变。'),
('legal-hard-22','legal-hard-22_identity_denominator.json','最终取替换分母后的计算，0.0097→0.0555；未拿中间分母本身当答案。类别不变。'),
('wildfire-hard-17','wildfire-hard-17_id_diagnostic.json','034匹配NWS ID得到759行均值4830.852437417655，原final_answer(round(e.mean(),2))必须保留2位，终点4830.85，差0.05；034文字用round1称完全对齐不成立。仅按实际监测站筛选仍减差1513.48，Intent主因不变。'),
('wildfire-easy-9','wildfire-easy-9_retry.json','成功retry计算最终斜率，与子任务算术一致；此题参考冲突类别不依改动常量。'),
]
rows=[]
for id,file,decision in checks:
 d=load(file);b=blocks(id)
 assert d.get('error') is None,(id,d.get('error'))
 rows.append({'id':id,'source':'records/034_checks/'+file,'source_sha256':hashlib.sha256((R/'records/034_checks'/file).read_bytes()).hexdigest(),'original_final_answer':b['final_answer'],'reused_endpoint':d['answer'],'decision':decision,'diagnostic_suffix':d.get('diagnostic_suffix',''),'changed_source':d.get('change')})
# Numerical list inventory: includes every numeric-list final in the036 population.
numeric=[]
for o in csv.DictReader((R/'records/034_objects.csv').open()):
 if o['benchmark']!='KramaBench' or o['主要原因']=='未交卷':continue
 b=blocks(o['对象编号'])
 try:a=json.loads(b['final_answer']);g=json.loads(b['gold_answer'])
 except (ValueError,KeyError):continue
 if not isinstance(a,list) or not a or not all(type(v) in (int,float) for v in a):continue
 assert isinstance(g,list) and len(a)==len(g)
 s=sum(abs(x-y) for x,y in zip(a,g));id=o['对象编号'];entry={'id':id,'baseline':a,'gold':g,'numeric_scale':s}
 if id=='astronomy-easy-6':entry.update(verdict='口径变化影响结论，见独立factorial重算',source='records/036_checks/astronomy-easy-6_scales.json')
 elif id=='astronomy-hard-8':
  alt=load('astronomy-hard-8_chrono70_retry.json')['answer'];entry.update(candidate=alt,candidate_scale=sum(abs(x-y) for x,y in zip(alt,g)),verdict='口径变化不影响结论：候选全属Choice；该方案不是独立单改，不能用接近程度强排候选',source='records/034_checks/astronomy-hard-8_chrono70_retry.json')
 elif id=='wildfire-hard-16':entry.update(output_only_round3=[round(x,3) for x in a],after_scale=sum(abs(round(x,3)-y) for x,y in zip(a,g)),verdict='口径变化不影响结论：输出层round3与gold相等，题面未规定3位，其他类别不变',source='records/034_checks/form_checks.json')
 else:raise ValueError(id)
 numeric.append(entry)
# Recompute Boolean endpoints from recorded numerical rates, not fixed final literals.
b=load('environment-hard-18_baseline_rates.json')['answer'];s=load('environment-hard-18_scope_only.json')['answer'];booleans=[]
def signs(values):return [(v>u)-(v<u) for u,v in zip(values,values[1:])]
for label,water,rain in [('baseline',b['exceedance'],b['rain']),('scope_only',s['rates'],s['rain'])]:
 water=[v for k,v in sorted(water.items())];rain=[v for k,v in sorted(rain.items())];booleans.append({'variant':label,'water':water,'rain':rain,'final':signs(water)==signs(rain)})
booleans.extend({'variant':v,'final':load('environment-hard-18_'+v+'.json')['answer']} for v in ['normalize_only','combination'])
(O/'endpoint_audit.json').write_text(json.dumps({'checks':rows,'numerical_lists':numeric,'environment_hard_18_boolean_endpoints':booleans,'wildfire_hard_17':{'original_rounding':2,'baseline':3317.37,'gold':4830.9,'new_endpoint':round(4830.852437417655,2),'baseline_scale':abs(3317.37-4830.9),'new_scale':abs(round(4830.852437417655,2)-4830.9)},'form_only':'034 form_checks 的纯输出变换按第7节豁免重算；不作数据处理单改证据。'},ensure_ascii=False,indent=2))
print(json.dumps(numeric,ensure_ascii=False,indent=2))
