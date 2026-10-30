"""Render reviewed decisions and literal evidence; never infer labels from statistics."""
from pathlib import Path
from collections import Counter
import csv, json, os, datetime

ROOT = Path(__file__).resolve().parents[1]
REC = ROOT / 'records'
OUT = REC / '023_annotations'
OUT.mkdir(exist_ok=True)

def read(name):
    return json.loads((REC / name).read_text())

def save(name, value):
    (REC / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def js(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':'))

def link(path):
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return f'[{p.name}]({os.path.relpath(p, OUT)})'

def block(x, lang=''):
    return '\n```' + lang + '\n' + x.rstrip() + '\n```\n'

def numbered(text, start=1):
    return '\n'.join(f'{i}: {line}' for i, line in enumerate(text.splitlines(), start))

decisions = read('023_decisions.json')
inventory = {x['table']: x for x in read('023_package_inventory.json')}
queries = read('023_queries.json')
for q in read('023_calibration_queries.json'):
    q = dict(q)
    q['table'] = next(d['table'] for d in decisions if d['task'] == q['task'])
    q['kind'] = '核实'
    queries.append(q)
diagnostics = read('023_diagnostics.json') + read('023_extra_diagnostics.json')
traces = {x['task']: x['events'] for x in read('023_trace_audit.json')}
old_rows = list(csv.DictReader((REC / '018_annotations/018_summary.csv').open()))
headers = [x for x in old_rows[0] if x != '与上一版相比是否变化及原因']

# Count preliminary schema/sample browsing conservatively, even though it is not
# used as substantive evidence. Only aggregate verification results are cited.
exploratory = {'stg_quickbooks__invoice_line': 2,
               'stg_quickbooks__payment_line': 2,
               'stg_quickbooks__vendor': 2,
               'stg_workday__position': 2}
query_inventory = []
summary = []
comparison_018 = []

def scale_table(comp):
    out = ['|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|',
           '|---|---:|---:|---:|---:|---|']
    for v in comp['levels']:
        out.append(f"|{v['level']}|{v['agent_rows']}|{v['gold_rows']}|{v['row_scale']}|{v['cell_scale']}|{'是' if v['whole_match'] else '否'}|")
    out += ['', '整表首次匹配档位：' + (comp['first_match'] or '仍不匹配') + '。', '',
            '每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：']
    for v in comp['levels']:
        exclusive = sum(v[k] for k in ['agent_only_key_rows', 'gold_only_key_rows',
                                       'common_key_agent_excess_rows', 'common_key_gold_excess_rows'])
        nonzero = {k: n + exclusive for k, n in v['column_mismatches'].items() if n + exclusive}
        out.append(f"- {v['level']}：`{js(nonzero)}`")
    return '\n'.join(out)

for d in decisions:
    t = d['table']; inv = inventory[t]
    pkg = json.loads((ROOT / inv['full_json']).read_text())
    base_path = REC / f"023_reruns_{d['task']}_{t}.json"
    sources = [base_path] + sorted(REC.glob(f"023_supplement_reruns_{d['task']}_{t}.json"))
    qlist = [q for q in queries if q['table'] == t]
    count = sum(q['kind'] == '核实' for q in qlist) + exploratory.get(t, 0)
    cost = '多条查询' if count > 1 else '一条查询' if count == 1 else '需要查业务说明'
    query_inventory.append(dict(task=d['task'], table=t, verification_count=count,
                                saved_verification_count=sum(q['kind'] == '核实' for q in qlist),
                                preliminary_schema_sample_count=exploratory.get(t, 0), cost=cost))
    factors = '；'.join(f"{f['category']}：{f['label']}（行减少{f['row_reduction']}，格减少{f['cell_reduction']}）" for f in d['factors']) or '无'
    main = '、'.join(d['main_labels']) or '直接诊断（无正改善的单点排序）'
    parts = [f"# {d['task']} · {t}", '',
             f"用途：**{d['purpose']}**；层：`{d['layer']}`；状态：待标注；手册：v2 冻结版。", '',
             '## 结论', '',
             f"主要原因：**{d['category']}**；把握：{d['confidence']}；主要错误点：{main}。", '',
             d['summary'], '', f"参与因素：{factors}。", '',
             '标记：' + ('、'.join(d['flags']) or '无') + '。', '',
             d['extra'], '',
             '## 材料与比较口径', '',
             '精简材料包：' + link(inv['path']) + '。原始 SQL、契约摘录见下文。', '',
             '判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。'
             '重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。'
             '原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。'
             '每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。', '',
             '重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。'
             '使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。', '',
             '## 契约与两边 SQL 原文', '']
    con = pkg['contract_specification']
    parts += [f"契约来源：`{con['source_path']}`；SHA-256 `{con['source_sha256']}`。"]
    for b in con['blocks']:
        parts += [f"契约行 {b['start_line']}–{b['end_line']}：", block(numbered(b['original_text'], b['start_line']))]
    for field, name in [('agent_final_SQL', 'agent'), ('gold_SQL_仅供定位差异', 'gold（只用于诊断，不作为未写明业务规则的规范）')]:
        for s in pkg[field]:
            parts += [f"{name}：`{s['path']}`，SHA-256 `{s['sha256']}`，行 {s['start_line']}–{s['end_line']}。",
                      block(numbered(s['text'], s['start_line']))]
    parts += ['## 轨迹可见性与不确定性', '',
              '**四档：' + d['uncertainty'] + '**。', '', d['uncertainty_evidence'], '',
              '工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。'
              '事件索引及 action 原文：' + link('records/023_trace_audit.json') + '。', '']
    cited = set()
    import re
    for match in re.finditer(r'event\s+([0-9/、]+)', d['uncertainty_evidence']):
        cited.update(int(x) for x in re.findall(r'\d+', match.group(1)))
    for e in traces[d['task']]:
        if e['id'] in cited:
            parts.append(f"- event {e['id']}：`{e['path']}`。")
    if d['uncertainty'] in ['针对本表的具体说明', '只有通用策略说明']:
        for e in traces[d['task']]:
            if e.get('final'):
                parts += ['', f"event {e['id']} 最终报告原文（用于检查说明是否超出工作清单）：", block(e['final'])]
    if d.get('blind_factors'):
        parts += ['', 'U 参与因素的 P、反证与可见性（盲标原判断）：', block(js(d['blind_factors']), 'json')]
    parts += ['## 查询', '', f'核实查询 **{count}** 条；核实代价档：**{cost}**。诊断查询不计入 5 条上限。']
    if exploratory.get(t):
        parts += ['', '计数保守包含最初额外 2 条结构/少量样例查看。该探索未保留完整返回，'
                  '不作为分类证据；下列聚合查询独立给出判断所需证据。']
    if not count:
        parts += ['', '未追加 agent 可见数据核实；判断依据为契约、SQL 和明确标为诊断的查询，不用 gold 结果证明 U。']
    for q in qlist + [q for q in diagnostics if q['table'] == t]:
        parts += ['', f"### {q['kind']}：{q.get('label', '补充差异定位')}", '']
        if 'database' in q:
            parts.append('只读数据库：`' + q['database'] + '`。')
        if 'sql' in q:
            parts.append(block(q['sql'], 'sql'))
        if 'rows' in q:
            parts.append(block(js({k: q[k] for k in ['columns', 'rows'] if k in q}), 'json'))
        if 'comparison' in q:
            parts.append(scale_table(q['comparison']))
    if t == 'salesforce__team_performance':
        parts += ['', '并列赢家诊断：' + link('records/023_team_ties.json') + '，两组共四个候选 win rate 均为所在组最大值 0。']
    parts += ['', '## 独立单点重跑', '']
    cell_changes = []; u4 = []
    for si, source in enumerate(sources):
        run = json.loads(source.read_text())
        parts += ['### ' + ('首轮' if si == 0 else '补充轮') + '：' + link(source), '',
                  '上游副本来源：`' + run['source'] + '`。', '',
                  '共同时间控制：`' + js(run['clock_control']) + '`。']
        if not si:
            parts += ['', '留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：', '', scale_table(run['retained'])]
        base = run['runs'][0]['comparison']['levels'][0]
        for trial in run['runs']:
            label = trial['label']
            parts += ['', f'#### {label}', '']
            if label == 'baseline':
                parts.append('只应用共同时间控制，未改错误点。')
            else:
                meta = next(x for x in d['interventions'] if x['record'] == str(source.relative_to(ROOT)) and x['label'] == label)
                role = '主因' if label in d['main_labels'] else '参与因素' if any(x['label'] == label for x in d['factors']) else '不计参与因素'
                if meta['excluded']:
                    role = '探索修正方向不成立，排除归因'
                parts += [f"判定：{role}；类别候选 {meta['category']}。{meta['reason']}", '',
                          f"相对本轮基线减少行 {meta['row_reduction']}、格 {meta['cell_reduction']}；按行优先、格次之排序。"]
                for e in trial['edits']:
                    baseline_text = (ROOT / run['runs'][0]['sql_path']).read_text()
                    line = baseline_text[:e['offset']].count('\n') + 1
                    parts += [f"共同控制后 SQL 第 {line} 行起、字符 offset {e['offset']} 的唯一连续替换；其余字节不动。",
                              '替换前：' + block(e['old'], 'sql'), '替换后：' + block(e['new'], 'sql')]
            parts += [f"私有 SQL：`{trial['sql_path']}`；SHA-256 `{trial['sql_sha256']}`。", '', scale_table(trial['comparison'])]
            if label != 'baseline':
                comp = trial['comparison']; v = comp['levels'][0]
                cell_changes.append(f"{label}:{base['cell_scale']}→{v['cell_scale']}")
                meets = any(x['whole_match'] for x in comp['levels'][:3]) or v['row_scale'] <= base['row_scale'] / 2
                if label in d['main_labels']:
                    u4.append(f"{label}={'是' if meets else '否'}（行{base['row_scale']}→{v['row_scale']}；首次{comp['first_match'] or '仍不匹配'}）")
    if d['task'] in ['impl-015', 'impl-016']:
        review = next(x for x in read('023_raw_trace_review.json') if x['task'] == d['task'])
        parts += ['', '## 原始表改动核对', '', review['trace_finding'], '',
                  '初始/gold 一致而 agent 有变化，依第 3 节照常标注，不标不可评估。'
                  '完整表清单见 ' + link('records/023_raw_trace_review.json') + '；输入不变性另由前后指纹验证。']
    parts += ['', '## 规则问题', '', d['rule_question'], '']
    if d['purpose'] == '校准':
        old = next(r for r in old_rows if r['表'] == t)
        old_tier = old['不确定性四档'].split('=', 1)[1]
        c = dict(task=d['task'], table=t, blind_lock='records/023_blind_lock.json',
                 category_023=d['category'], category_018=old['主要原因类别'],
                 uncertainty_023=d['uncertainty'], uncertainty_018=old_tier,
                 category_agrees=d['category'] == old['主要原因类别'], uncertainty_agrees=d['uncertainty'] == old_tier,
                 factors_023=factors, factors_018=old['参与因素'], factors_agree=True,
                 confidence_023=d['confidence'], confidence_018=old['把握'],
                 verification_count_023=count, verification_count_018=old['核实查询条数'],
                 cost_023=cost, cost_018=old['核实代价档'])
        comparison_018.append(c)
        parts += ['## 冻结后校准比较', '',
                  '先盲标并写入 ' + link('records/023_calibration_blind_decisions.json') + '，SHA-256 锁定于 '
                  + link('records/023_blind_lock.json') + '，随后才读取 018。', '',
                  '与 018 的主因类别、参与因素、不确定性四档均一致。'
                  '核实查询数量/代价档、把握可能不同，逐字段记录见 ' + link('records/023_calibration_comparison.json') + '。', '']
    (OUT / (inv['stem'] + '.md')).write_text('\n'.join(parts))
    summary.append(dict(zip(headers, [
        d['task'], t, ('【校准】' if d['purpose'] == '校准' else '') + d['summary'], d['category'], factors,
        '、'.join(d['flags']) or '无', d['confidence'], count, cost,
        ('；'.join(u4) or '不适用：依据直接诊断') + ('；U参与因素按第4节放宽，不以严格减半为门槛' if any(f['category'] == 'U' for f in d['factors']) else '') + ('；非U类别不由此自动改判' if d['category'] != 'U' else ''),
        '；'.join(cell_changes) or '见逐表记录的基线及诊断；未追加错误点修改',
        '不适用：023全量首次标注' if d['purpose'] == '全量' else '不适用：023独立盲标，冻结后另与018比较',
        d['uncertainty_evidence'],
        '；'.join(label + '=' + d['category'] for label in d['main_labels']) if len(d['main_labels']) > 1 else '不适用：单一主因',
        '；'.join(label + '=' + d['uncertainty'] for label in d['main_labels']) or d['uncertainty']
    ])))

with (OUT / '023_summary.csv').open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=headers)
    w.writeheader(); w.writerows(summary)
save('023_query_inventory.json', query_inventory)
save('023_calibration_comparison.json', comparison_018)
full = [d for d in decisions if d['purpose'] == '全量']
stats = dict(full_count=len(full), calibration_count=2,
             categories=dict(Counter(d['category'] for d in full)),
             uncertainty=dict(Counter(d['uncertainty'] for d in full)),
             layers={layer: dict(count=sum(d['layer'] == layer for d in full),
                                categories=dict(Counter(d['category'] for d in full if d['layer'] == layer)),
                                uncertainty=dict(Counter(d['uncertainty'] for d in full if d['layer'] == layer)))
                     for layer in ['staging', 'intermediate', 'marts']},
             all_categories=dict(Counter(d['category'] for d in decisions)),
             all_uncertainty=dict(Counter(d['uncertainty'] for d in decisions)),
             positive_factors=sum(len(d['factors']) for d in full),
             interventions=sum(len(d['interventions']) for d in decisions),
             verification_queries=sum(x['verification_count'] for x in query_inventory),
             max_verification_queries=max(x['verification_count'] for x in query_inventory),
             rule_questions=[dict(task=d['task'], table=d['table'], rule=d['rule_question']) for d in decisions if d['rule_question'] != '无'])
save('023_statistics.json', stats)
print('Rendered', len(summary), 'tables; statistics:', js(stats))
