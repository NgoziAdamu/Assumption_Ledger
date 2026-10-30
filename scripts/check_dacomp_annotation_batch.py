"""检查一批 Codex 全量标注结果（019～024）。用法：python3 -I check_batch.py <repo> <批号> [--as-trial]
只读仓库文件，不打开数据库。输出：分布、可疑标注、校准对比、随机抽样，以及一份 JSON 供台账使用。"""
import csv, json, re, sys, random, collections, glob, os

repo, batch = sys.argv[1], sys.argv[2]
R = lambda p: os.path.join(repo, p)

BATCHES = {'019': (range(1, 6), ['impl-008', 'impl-021']),
           '020': (range(6, 8), ['impl-002', 'impl-025']),
           '021': (range(8, 12), ['impl-013', 'impl-030']),
           '022': (range(12, 15), ['impl-005', 'impl-027']),
           '023': (range(15, 22), ['impl-009', 'impl-024']),
           '024': (range(22, 31), ['impl-006', 'impl-016']),
           '018': (range(1, 31), [])}
TIERS = ['针对本表的具体说明', '只有通用策略说明', '看到了但没提', '没有迹象']
CATS = ['U', 'D', 'C', 'A', 'I', 'O', 'X']


def read_csv(p):
    return list(csv.DictReader(open(p, encoding='utf-8-sig')))


def col(row, *keys):
    for k in row:
        for key in keys:
            if key in k:
                return row[k] or ''
    return ''


# ---------- 载入 ----------
cands = sorted(glob.glob(R(f'records/{batch}_annotations/*summary*.csv')) + glob.glob(R(f'records/{batch}_*summary*.csv')))
if not cands:
    sys.exit(f'找不到 {batch} 的汇总 CSV')
rows = read_csv(cands[0])
trial = {r['题目']: r for r in read_csv(R('records/018_annotations/018_summary.csv'))}
status = read_csv(R('records/013_statuses.csv'))
layer_of = {(r['task'], r['table']): r['layer'] for r in status}

# 015：直接读取的 raw 表 gold≠agent 且 agent=initial → 预期不可评估；间接下游（CS 口径用 gold 上游）→ 预期照常标注
cmp = collections.defaultdict(dict)
for r in read_csv(R('records/015_raw_comparisons.csv')):
    cmp[(r['task'], r['raw_table'])][r['comparison']] = r
exp_direct, exp_indirect, agent_mod = set(), set(), set()
for line in open(R('records/015_pending_downstream.jsonl'), encoding='utf-8'):
    d = json.loads(line)
    c = cmp[(d['task'], d['raw_table'])]
    gi = c.get('gold_vs_initial', {}).get('different') == 'True'
    ga = c.get('gold_vs_agent', {}).get('different') == 'True'
    for t in d['pending_downstream_tables']:
        k = (t['task'], t['table'])
        if gi and ga:
            (exp_direct if t['direct'] else exp_indirect).add(k)
        elif ga:
            agent_mod.add(k)
exp_indirect -= exp_direct

rng_tasks, calib = BATCHES[batch]
expected = {(r['task'], r['table']) for r in status if r['status'] == '待标注' and int(r['task'][-3:]) in rng_tasks}
if batch != '018':
    expected -= {(t, trial[t]['表']) for t in trial if int(t[-3:]) in rng_tasks}
    expected |= {(t, trial[t]['表']) for t in calib}


def main_cat(s):
    s = s.strip()
    if s.startswith('多因并列'):
        return '多因并列'
    if s.startswith('不可评估'):
        return '不可评估'
    m = re.match(r'([UDCAIOX])\b', s)
    return m.group(1) if m else s


def tied(s):
    m = re.search(r'多因并列[（(]([^）)]*)', s)
    return re.findall(r'[UDCAIOX]', m.group(1)) if m else []


def item_cats(row):  # 并列项类别：key=A；key=C
    return dict(re.findall(r'([^；;=\s]+)\s*=\s*([UDCAIOX])\b', col(row, '并列项类别')))


def tiers(row):
    v = col(row, '不确定性四档').strip()
    if v in TIERS:
        return {'(主项)': v}
    return dict(re.findall(r'([^；;=\s]+)\s*=\s*(' + '|'.join(TIERS) + ')', col(row, '不确定性四档')))


def contrib_cats(s):
    return re.findall(r'(?:^|[；;])\s*([UDCAIOX])\s*[：:]', s)


# ---------- 逐行检查 ----------
flags = collections.defaultdict(list)
dist_main, dist_layer, dist_tier_items, tier_tables = collections.Counter(), collections.defaultdict(collections.Counter), collections.Counter(), collections.Counter()
u_involved, a_items, a_silent_main = set(), 0, 0
got = set()
for r in rows:
    task, tab = r['题目'], r['表']
    key = (task, tab)
    got.add(key)
    m_raw = col(r, '主要原因类别')
    m = main_cat(m_raw)
    lay = layer_of.get(key, '?')
    dist_main[m] += 1
    dist_layer[lay][m] += 1
    ic = item_cats(r)
    tc = tied(m_raw) or (list(ic.values()) if m == '多因并列' else [])
    cc = contrib_cats(col(r, '参与因素'))
    tr = tiers(r)
    for v in tr.values():
        dist_tier_items[v] += 1
    for t in set(tr.values()):
        tier_tables[t] += 1
    desc = col(r, '一句话描述')
    q = col(r, '核实查询条数').strip()
    qn = int(re.match(r'\d+', q).group()) if re.match(r'\d+', q) else None
    rerun = col(r, '重跑是否满足')
    scale = col(r, '格子数口径规模变化')
    all_cats = ([m] if m in CATS else []) + tc + list(ic.values()) + cc
    if 'U' in all_cats:
        u_involved.add(key)
        if not qn:
            flags[key].append(f'涉及 U，但核实查询条数={q or "空"}')
        if not scale.strip() or re.match(r'^\s*(无|不适用|基线\d+；无)', scale):
            flags[key].append('涉及 U，但没有单改重跑的规模变化')
    if m == 'U' and re.match(r'\s*否', rerun):
        flags[key].append(f'主要原因 U，但第 4 个条件写"否"：{rerun[:80]}')
    if m == 'U' and not rerun.strip():
        flags[key].append('主要原因 U，第 4 个条件字段为空')
    # A 相关
    a_keys = [k for k, v in ic.items() if v == 'A']
    if m == 'A':
        a_keys = list(tr.keys()) or ['(主项)']
    if m == 'A' or 'A' in tc or 'A' in cc:
        if m == 'A' and not tr:
            flags[key].append('主要原因 A，但四档字段没有可解析的值')
        for k in a_keys:
            if k in ic or m == 'A':
                if k not in tr and tr:
                    flags[key].append(f'A 项 {k} 没有对应四档')
        if re.search(r'做错|错误地|弄错|错把|错用|错选|本应|应当|应该', desc):
            flags[key].append(f'涉及 A，描述含评价性措辞：{desc[:100]}')
    if m == 'A':
        a_items += 1
        if tr and all(v != '针对本表的具体说明' for v in tr.values()):
            a_silent_main += 1
    if m == 'X' or 'X' in tc or 'X' in cc or 'X' in ic.values():
        flags[key].append('用了 X')
    if m == '多因并列':
        if len(tc) < 2:
            flags[key].append('多因并列但列出的并列类别少于 2 个')
        if len(set(tc)) == 1:
            flags[key].append('多因并列但所有并列项同类（v2 应直接记该类）')
        if not ic:
            flags[key].append('多因并列但"并列项类别"不可解析')
    # 不可评估 与 015
    if m == '不可评估' and key not in exp_direct:
        flags[key].append('标不可评估，但 015 显示其直接读取的 raw 表不属于"gold 原始数据不同"' + ('（只是间接下游，CS 口径用 gold 上游）' if key in exp_indirect else '') + ('（agent 自己改过原始数据，应照常标注）' if key in agent_mod else ''))
    if m != '不可评估' and key in exp_direct:
        flags[key].append('015 显示直接读取的 raw 表在 gold 中不同，但未标不可评估（需看诊断）')
    # 四档
    if not tr:
        flags[key].append('四档字段为空或不可解析')
    if '针对本表的具体说明' in tr.values():
        md = glob.glob(R(f'records/{batch}_annotations/*{task}*{tab}*.md')) or glob.glob(R(f'records/{batch}_annotations/*{task}*.md'))
        txt = open(md[0], encoding='utf-8').read() if md else ''
        secs = re.split(r'\n(?=#{2,4} )', txt)
        spec = [x for x in secs if re.match(r'#{2,4} [^\n]*针对本表的具体说明', x)]
        ev = col(r, 'agent 是否意识到')
        csv_ok = bool(re.search(r'event\s*\d+', ev)) and len(ev) > 40
        ok = csv_ok or bool(spec) and all(re.search(r'事件', x) and re.search(r'```[a-z]*\n\s*\S', x) for x in spec)
        if not ok:
            flags[key].append('四档为"针对本表的具体说明"，逐表文件里附近找不到事件编号加引号原句')

missing, extra = expected - got, got - expected
dups = [k for k, v in collections.Counter((r['题目'], r['表']) for r in rows).items() if v > 1]

# ---------- 校准 ----------
calib_out = []
for t in calib:
    b = [r for r in rows if r['题目'] == t and r['表'] == trial[t]['表']]
    if not b:
        calib_out.append((t, '本批缺少校准表'))
        continue
    b, a = b[0], trial[t]
    same_main = main_cat(col(b, '主要原因类别')) == main_cat(a['主要原因类别']) and sorted((tied(col(b, '主要原因类别')) or list(item_cats(b).values()))) == sorted(tied(a['主要原因类别']))
    same_contrib = sorted(contrib_cats(col(b, '参与因素'))) == sorted(contrib_cats(a['参与因素']))
    same_tier = sorted(tiers(b).values()) == sorted(tiers(a).values())
    calib_out.append((t, {'表': a['表'], '主要原因': (col(b, '主要原因类别')[:60], a['主要原因类别'][:60], same_main),
                          '参与因素类别': (contrib_cats(col(b, '参与因素')), contrib_cats(a['参与因素']), same_contrib),
                          '四档': (sorted(tiers(b).values()), sorted(tiers(a).values()), same_tier)}))

# ---------- 必读和随机抽样 ----------
must = set(flags) | {(r['题目'], r['表']) for r in rows if main_cat(col(r, '主要原因类别')) == 'U'} | {(r['题目'], r['表']) for r in rows if '针对本表的具体说明' in tiers(r).values()}
pool = sorted(got - must - {(t, trial[t]['表']) for t in calib})
rng = random.Random(int('2026' + batch))
sample = rng.sample(pool, min(3, len(pool)))

out = {'batch': batch, 'csv': os.path.relpath(cands[0], repo), 'rows': len(rows), 'expected': len(expected),
       'missing_n': len(missing), 'missing': [f'{a} {b}' for a, b in sorted(missing)][:20], 'extra': [f'{a} {b}' for a, b in sorted(extra)], 'dups': dups,
       'main': dict(dist_main), 'by_layer': {k: dict(v) for k, v in dist_layer.items()},
       'tier_items': dict(dist_tier_items), 'tier_tables': dict(tier_tables),
       'u_involved': len(u_involved), 'A_main_not_specific': a_silent_main,
       'flags': {f'{k[0]} {k[1]}': v for k, v in flags.items()},
       'calibration': calib_out, 'must_read': sorted(f'{k[0]} {k[1]}' for k in must),
       'random_sample': [f'{k[0]} {k[1]}' for k in sample],
       'sample_rule': f'random.Random({int("2026" + batch)}).sample(按题目+表名排序的、不在必读名单且非校准表的 {len(pool)} 张, 3)'}
print(json.dumps(out, ensure_ascii=False, indent=1))
