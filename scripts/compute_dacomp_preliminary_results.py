"""计算 DAComp DE-Impl 全量标注的初步结果（2026-10-30 用户采用的"建议版"）。
用法：python3 -I compute_preliminary_results.py <仓库根目录>
只读 records/*_annotations/*_summary.csv，不打开数据库。

建议版 = Codex 原标注（018～024）＋ 025 更正 ＋ Claude 对争议项的建议处理（见 FIX）。
大类：缺失证据 = 未核实假设 U＋没照契约做 C＋悄悄降级 D；歧义 A；代码写错 I；不计入 = O、X、不可评估。
"""
import csv, re, sys, random, collections, os

repo = sys.argv[1]
BIG = {'U': '缺失证据', 'C': '缺失证据', 'D': '缺失证据', 'A': '歧义', 'I': '代码写错',
       'O': '不计入', 'X': '不计入', '不可评估': '不计入'}
TI = '针对本表的具体说明|只有通用策略说明|看到了但没提|没有迹象'
SPEC = [('018', None), ('019', None), ('020', ('impl-006', 'impl-007')),
        ('021', ('impl-008', 'impl-009', 'impl-010', 'impl-011')),
        ('022', ('impl-012', 'impl-013', 'impl-014')),
        ('023', tuple(f'impl-0{i}' for i in range(15, 22))),
        ('024', tuple(f'impl-0{i}' for i in range(22, 31)))]
# 025 更正 + 建议版处理：(题目, 表) -> (主要原因项列表, 参与因素类别列表或 None 表示不改)
FIX = {
    ('impl-010', 'int_hubspot__owner_performance_metrics'): ([('O', '看到了但没提')], ['O', 'C', 'O']),
    ('impl-010', 'hubspot__sales_performance_dashboard'): ([('O', '看到了但没提')], ['O']),
    ('impl-010', 'hubspot__sales_rep_performance'): ([('O', '看到了但没提')], ['A', 'A', 'A', 'O', 'O']),
    ('impl-003', 'customer360__customer'): ([('A', '只有通用策略说明')], None),
    ('impl-006', 'int_ad_reporting__account_report'): ([('D', '只有通用策略说明')], None),
    ('impl-014', 'qualtrics__user_cohort_analysis'): ([('A', '针对本表的具体说明')], None),
    ('impl-012', 'marketo__calendar_spine'): ([('A', '只有通用策略说明')], None),
}
CONTRIB_U_TO_A = {('impl-008', 'int_asana__project_health_indicators')}
COMBINATION_ONLY = {('impl-030', 'stg_zuora__invoice_payment')}


def items(r):
    m = r['主要原因类别']
    if m.startswith('不可评估'):
        return [('不可评估', None)]
    tv = dict(re.findall(r'([^；;=\s*：]+)\s*[=：]\s*(' + TI + ')', r['不确定性四档']))
    one = re.findall(TI, r['不确定性四档'])
    if m.startswith('多因并列'):
        return [(c, tv.get(k, one[0] if len(set(one)) == 1 else None))
                for k, c in re.findall(r'([^；;=\s]+)\s*=\s*([UDCAIOX])\b', r['并列项类别'])]
    c = re.match(r'([UDCAIOX])', m).group(1)
    return [(c, one[0] if len(set(one)) == 1 else '混合')]


def contribs(r):
    s = r['参与因素']
    return re.findall(r'(?:^|[；;])\s*([UDCAIO])\s*[：:]', s) + re.findall(r'=\s*([UDCAIO])\b', s)


T = []
for b, tasks in SPEC:
    path = os.path.join(repo, f'records/{b}_annotations/{b}_summary.csv')
    for x in csv.DictReader(open(path, encoding='utf-8-sig')):
        if b != '018' and ('校准' in x['一句话描述'][:6] or x.get('标记', '') == '校准'):
            continue
        if tasks and x['题目'] not in tasks:
            continue
        k = (x['题目'], x['表'])
        it, co = items(x), contribs(x)
        if k in FIX:
            it = FIX[k][0]
            co = FIX[k][1] if FIX[k][1] is not None else co
        if k in CONTRIB_U_TO_A:
            co = ['A' if c == 'U' else c for c in co]
        T.append(dict(task=k[0], table=k[1], items=it, contribs=co, combo=k in COMBINATION_ONLY))
assert len(T) == 283, len(T)


def big(t):
    s = set(BIG[c] for c, _ in t['items'])
    return s.pop() if len(s) == 1 else '跨大类并列'


ev_f = lambda t: big(t) != '不计入' and not t['combo']
allc = lambda t: set(c for c, _ in t['items']) | set(t['contribs'])
silentA = lambda t: any(c == 'A' and tt != '针对本表的具体说明' for c, tt in t['items'])
DEFS = {
    '缺失证据（主要原因）': lambda t: big(t) == '缺失证据',
    '缺失证据（参与其中）': lambda t: any(BIG[c] == '缺失证据' for c in allc(t)),
    '没说出来的歧义（主要原因）': lambda t: big(t) == '歧义' and silentA(t),
    '没说出来的歧义（参与其中，限主因与并列项）': silentA,
    '未核实假设 U（主要原因）': lambda t: [c for c, _ in t['items']] == ['U'],
    '未核实假设 U（参与其中）': lambda t: 'U' in allc(t),
    '代码写错（主要原因）': lambda t: big(t) == '代码写错',
}
ev = [t for t in T if ev_f(t)]
print('分母（去掉不计入和只能组合修复）:', len(ev))
print('主要原因大类:', dict(collections.Counter(big(t) for t in ev)))
random.seed(20261030)
byt = collections.defaultdict(list)
for t in T:
    byt[t['task']].append(t)
tasks = sorted(byt)
for name, f in DEFS.items():
    n = sum(1 for t in ev if f(t))
    bs = []
    for _ in range(5000):
        s = [t for tk in random.choices(tasks, k=len(tasks)) for t in byt[tk] if ev_f(t)]
        bs.append(sum(1 for t in s if f(t)) / len(s))
    bs.sort()
    print(f'{name}: {n}/{len(ev)} = {n / len(ev):.1%}  按题重抽样95%范围 {bs[125]:.1%}～{bs[4875]:.1%}')
# 悄悄出错（严格定义）：agent 自己的错 + 所在题宣称完成（排除 impl-011）+ 主要原因项都没有具体说明
own = [t for t in ev if t['task'] != 'impl-011']
spec_all = [t for t in own if all(tt == '针对本表的具体说明' for _, tt in t['items'])]
print('宣称完成的题里 agent 自己的错表:', len(own), '；悄悄出错:', len(own) - len(spec_all), '（交付表总数 1069）')
