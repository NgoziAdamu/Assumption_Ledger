"""Validate task023 coverage, literal one-location edits, scales and immutable inputs."""
from pathlib import Path
import csv, json, hashlib, re, subprocess, datetime

ROOT = Path(__file__).resolve().parents[1]
REC = ROOT / 'records'

def read(name):
    return json.loads((REC / name).read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check(condition, detail):
    assert condition, detail

inv = read('023_package_inventory.json')
dec = read('023_decisions.json')
scope = read('023_scope.json')
before = read('023_input_before.json')
after = read('023_input_after.json')
cases = {x['task']: x for x in read('013_cases.json')}
check(not after['changes'], after['changes'])
check(before['files'] == after['files'], 'input manifests differ')
check(len(before['files']) == 7688, 'fingerprint count')
lock = read('023_blind_lock.json')
check(sha(ROOT / lock['path']) == lock['sha256'], 'blind decisions changed')
check(not lock['prior_annotation_results_read_before_lock'], 'blind protocol')

statuses = list(csv.DictReader((REC / '013_statuses.csv').open()))
pilot = set()
for path in (REC / '013_packages').glob('*.md'):
    # Original pilot naming: 013_impl-NNN_<layer>_<table>.md.
    match = re.match(r'013_(impl-\d+)_(?:staging|intermediate|marts)_(.+)\.md$', path.name)
    if match:
        pilot.add(match.groups())
check(len(pilot) == 30, ('pilot', len(pilot)))
expected = {(x['task'], x['table']) for x in statuses if 'impl-015' <= x['task'] <= 'impl-021'
            and x['status'] == '待标注' and (x['task'], x['table']) not in pilot}
actual = {(x['task'], x['table']) for x in scope if x['purpose'] == '全量'}
check(actual == expected and len(actual) == 39, 'full scope')
cal = [('impl-009', 'stg_google_play__store_performance_country'),
       ('impl-024', 'stg_tiktok_ads__advertiser')]
check([(x['task'], x['table']) for x in scope if x['purpose'] == '校准'] == cal, 'cal scope')
check(len(dec) == 41 and len({x['table'] for x in dec}) == 41, 'decisions')
out = REC / '023_annotations'
check({p.stem for p in out.glob('*.md')} == {x['stem'] for x in inv}, 'Markdown coverage')
check(len(list((REC / '023_packages').glob('*.md'))) == 39, 'packages')
with (out / '023_summary.csv').open() as f:
    reader = csv.DictReader(f); headers = reader.fieldnames; rows = list(reader)
with (REC / '018_annotations/018_summary.csv').open() as f:
    oldheaders = csv.DictReader(f).fieldnames
check(headers == [x for x in oldheaders if x != '与上一版相比是否变化及原因'], 'CSV header')
check(len(rows) == 41, 'CSV count')
check([(r['题目'], r['表']) for r in rows[-2:]] == cal, 'cal last')
check(all(r['一句话描述'].startswith('【校准】') for r in rows[-2:]), 'cal labels')
check(all('【校准】' not in r['一句话描述'] for r in rows[:-2]), 'full labels')
check(all(0 <= x['verification_count'] <= 5 for x in read('023_query_inventory.json')), 'query limit')

original_sources = set()
baseline_hashes = {}; baseline_comparisons = {}; run_count = 0; interventions = 0
for path in sorted(REC.glob('023_*reruns_*.json')):
    x = json.loads(path.read_text()); table = x['basis']['table']; i = next(i for i in inv if i['table'] == table)
    pkg = json.loads((ROOT / i['full_json']).read_text())
    original_sources.update([x['source'], x['basis']['gold_database'], x['basis']['prediction_database'],
                             pkg['contract_specification']['source_path']])
    for role in ['agent_final_SQL', 'gold_SQL_仅供定位差异']:
        original_sources.update(s['path'] for s in pkg[role])
    check(before['completed_utc'] < x['started_utc'], ('snapshot timing', path.name))
    sql = Path(pkg['agent_final_SQL'][0]['path']).read_text()
    for e in x['clock_control']:
        sql, n = re.subn(e['pattern'], e['replacement'], sql, flags=re.I)
        check(n == e['count'], ('clock edit count', path.name))
    check(x['source'] == cases[i['task']]['agent_database'] if i['layer'] == 'staging'
          else x['source'] == x['basis']['gold_database'], ('CS/raw basis', table))
    for r in x['runs']:
        run_count += 1
        check('error' not in r, (path.name, r.get('error')))
        n = 0 if r['label'] == 'baseline' else 1
        check(len(r['edits']) == n, ('not one location', path.name, r['label']))
        interventions += n
        wanted = sql
        for e in r['edits']:
            check(wanted.count(e['old']) == 1 and wanted.index(e['old']) == e['offset'], ('replacement bounds', r['label']))
            wanted = wanted.replace(e['old'], e['new'], 1)
        working = ROOT / r['sql_path']
        check(working.is_relative_to(ROOT / 'data'), 'private SQL location')
        check(working.read_text() == wanted and sha(working) == r['sql_sha256'], ('bytes outside edit changed', r['label']))
        if not n:
            if table in baseline_hashes:
                check(baseline_hashes[table] == r['sql_sha256'], ('supplement baseline SQL', table))
                check(baseline_comparisons[table] == r['comparison'], ('supplement baseline result', table))
            baseline_hashes[table] = r['sql_sha256']; baseline_comparisons[table] = r['comparison']
        for v in r['comparison']['levels']:
            exclusive = sum(v[k] for k in ['agent_only_key_rows', 'gold_only_key_rows',
                                           'common_key_agent_excess_rows', 'common_key_gold_excess_rows'])
            check(v['row_scale'] == exclusive + v['common_key_different_rows_or_min_pairs'], 'row scale')
            check(v['cell_scale'] == sum(v['column_mismatches'].values()) + exclusive * len(v['column_mismatches']), 'cell scale')
            check(v['whole_match'] == (v['row_scale'] == 0) == (v['cell_scale'] == 0), 'whole match')
            check(set(v['column_mismatches']) == set(x['basis']['key_columns'] + x['basis']['comparison_columns']), 'full keyed columns')
        check(r['comparison']['first_match'] == next((v['level'] for v in r['comparison']['levels'] if v['whole_match']), None), 'first match')
missing_sources = sorted(p for p in original_sources if p not in before['files'])
derived_before = read('023_derived_input_before.json')
derived_after = read('023_derived_input_after.json')
derived_check = read('023_derived_recheck.json')
check(set(missing_sources) == set(derived_before['files']) and len(missing_sources) == 9, 'declared derived snapshot gap')
check(not derived_after['changes'] and derived_before['files'] == derived_after['files'], 'derived recheck immutability')
check(all(x['reread_matches_previously_recorded'] for x in derived_check['checks']), 'derived comparisons changed')
check(derived_before['completed_utc'] < derived_check['completed_utc'], 'derived recheck timing')
check(len(baseline_hashes) == 41 and interventions == 99 and run_count == 150, 'run counts')

for d in dec:
    candidates = [x for x in d['interventions'] if not x['excluded']]
    if d['main_ranking']:
        best = max((x['row_reduction'], x['cell_reduction']) for x in candidates)
        check(all((x['row_reduction'], x['cell_reduction']) == best for x in d['main_ranking']), ('main ranking', d['table']))
    check(all(x['row_reduction'] > 0 or x['row_reduction'] == 0 and x['cell_reduction'] > 0 for x in d['factors']), 'non-improving factor')
    row = next(x for x in rows if x['表'] == d['table'])
    check(row['主要原因类别'] == d['category'], 'CSV category')
    text = (out / (next(i['stem'] for i in inv if i['table'] == d['table']) + '.md')).read_text()
    for part in ['## 结论', '## 契约与两边 SQL 原文', '## 轨迹可见性与不确定性', '## 查询', '## 独立单点重跑', '## 规则问题']:
        check(part in text, ('missing section', d['table'], part))
check(all(x['category_agrees'] and x['uncertainty_agrees'] and x['factors_agree'] for x in read('023_calibration_comparison.json')), 'calibration conclusion')
tracked_changes = subprocess.check_output(['git', 'diff', '--name-only', '-z', 'HEAD'], cwd=ROOT, text=True).split('\0')
tracked_changes = [p for p in tracked_changes if p]
# Works before or after staging: newly added task023 files are allowed, old files never are.
def permitted(p):
    return p.startswith('records/023_') or p.startswith('notes/023_') or p.startswith('scripts/') and Path(p).stem.endswith('023')
check(all(permitted(p) for p in tracked_changes), ('old tracked edits', tracked_changes))
untracked = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '-z'], cwd=ROOT, text=True).split('\0')
untracked = [p for p in untracked if p]
check(all(permitted(p) for p in untracked), ('unrelated untracked files', untracked))
tracked = [p for p in subprocess.check_output(['git','ls-files','-z'],cwd=ROOT,text=True).split('\0') if p]
old_tracked_without_snapshot = [p for p in tracked if not permitted(p) and str(ROOT/p) not in before['files']]
for p in old_tracked_without_snapshot:
    committed = subprocess.check_output(['git','show','HEAD:'+p],cwd=ROOT)
    check(hashlib.sha256(committed).hexdigest() == sha(ROOT/p), ('old unsnapshotted tracked content',p))
result = dict(checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), result='PASS',
              full_tables=39, calibration_tables=2, markdown_files=41, new_packages=39,
              original_fingerprinted_files=7688, original_changes=after['changes'],
              required_original_sources_covered=len(original_sources), untracked_outside_scope=[],
              original_sources_in_first_snapshot=len(original_sources)-len(missing_sources),
              declared_late_snapshot_derived_databases=missing_sources,
              late_snapshot_limitation=derived_check['limitations'],
              derived_revalidation_before_after_unchanged=True,
              old_tracked_without_initial_file_snapshot=old_tracked_without_snapshot,
              old_tracked_without_snapshot_match_existing_git_HEAD=True,
              single_location_interventions=interventions, baseline_groups=51, executed_trials=run_count,
              supplemental_baseline_SQL_and_comparisons_equal=True, unchanged_bytes_outside_single_edit=True,
              CSV_header_equals_018_minus_last_column=True, calibration_last_two=True,
              blind_decisions_hash_matches=True, prior_labels_read_before_lock=False,
              full_key_columns_preserved=True, row_cell_scales_consistent=True, no_rerun_errors=True,
              max_verification_queries=max(x['verification_count'] for x in read('023_query_inventory.json')),
              classifications_ranked_by_rows_then_cells=True)
(REC / '023_validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False))
