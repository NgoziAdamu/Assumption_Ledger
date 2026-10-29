"""Task 015: independent metadata/multiset checks and original-file integrity."""

from collections import Counter, defaultdict, deque
import json
from pathlib import Path
import re
import subprocess

import duckdb

from check_dacomp_gold_raw import inventory, read_jsonl
from check_dacomp_constraints import open_readonly
from compare_dacomp_staging import fingerprint, quote
from complete_dacomp_comparisons import ROOT, RECORDS, save, stamp


def main():
    rows = read_jsonl(RECORDS/'015_raw_comparisons.jsonl')
    cases = json.loads((RECORDS/'015_cases.json').read_text())
    assert len(cases) == 30
    assert len({(r['task'], r['comparison'], r['raw_table']) for r in rows}) == len(rows)
    inventory_tables = 0
    hash_streams, hash_rows = 0, 0
    independent_content = []
    for case in cases:
        task = case['task']
        doc = json.loads((RECORDS/f'015_raw_{task}.json').read_text())
        for side in ('gold', 'initial', 'agent'):
            old = doc['sides'][side]
            new = inventory(case[side+'_database'], ROOT/'data/015_validation'/task/side)
            assert old['raw_schema_exists'] == new['raw_schema_exists']
            assert old['attached_read_only_source'] == new['attached_read_only_source']
            assert set(old['tables']) == set(new['tables'])
            for name, entry in old['tables'].items():
                for key in ('table_type', 'columns', 'row_count', 'read_error'):
                    assert entry[key] == new['tables'][name][key], (task, side, name, key)
                inventory_tables += 1
                if entry['content_hash']:
                    assert entry['content_hash'].get('sha256')
                    assert entry['content_hash']['rows_hashed'] == entry['row_count']
                    hash_streams += 1
                    hash_rows += entry['row_count']
        for row in doc['comparisons']:
            other = row['comparison'].removeprefix('gold_vs_')
            a, b = row['gold'], row[other]
            assert a == doc['sides']['gold']['tables'].get(row['raw_table'][4:])
            assert b == doc['sides'][other]['tables'].get(row['raw_table'][4:])
            if a and b and a['row_count'] is not None and a['row_count'] == b['row_count']:
                assert row['sorted_content_hash_equal'] is not None, (task, other, row['raw_table'])
            else:
                assert row['sorted_content_hash_equal'] is None
        # Native SQL multiset comparisons, independent of Python serialization:
        # every same-schema unequal hash plus one equal hash per comparison/task.
        for other in ('initial', 'agent'):
            eligible = [r for r in doc['comparisons'] if r['comparison'] == 'gold_vs_'+other and r['ordered_columns_and_types_equal'] is True and r['sorted_content_hash_equal'] is not None]
            selected = [r for r in eligible if r['sorted_content_hash_equal'] is False]
            selected += next(([r] for r in eligible if r['sorted_content_hash_equal'] is True), [])
            if not selected:
                continue
            scratch = ROOT/'data/015_validation'/task/'except_all'
            scratch.mkdir(parents=True, exist_ok=True)
            if doc['sides']['gold']['attached_read_only_source'] or doc['sides'][other]['attached_read_only_source']:
                # Stored raw views can refer to the literal external alias source.
                # Read in separate connections so attached other-side views never
                # accidentally resolve through the first side's source database.
                for row in selected:
                    name = row['raw_table'][4:]
                    sql = 'SELECT * FROM raw.'+quote(name)
                    with open_readonly(Path(case['gold_database']), scratch/'gold') as conn:
                        left = Counter(conn.execute(sql).fetchall())
                    with open_readonly(Path(case[other+'_database']), scratch/'other') as conn:
                        right = Counter(conn.execute(sql).fetchall())
                    counts = (sum((left-right).values()), sum((right-left).values()))
                    assert (counts == (0, 0)) == row['sorted_content_hash_equal']
                    independent_content.append({'task': task, 'comparison': row['comparison'], 'raw_table': row['raw_table'],
                                                'sql': sql, 'method': 'separate-read-only-connection typed row Counters (external view sources isolated)',
                                                'gold_only_rows': counts[0], 'other_only_rows': counts[1],
                                                'agrees_with_sorted_hash': True})
                continue
            with open_readonly(Path(case['gold_database']), scratch) as conn:
                conn.execute("SET TimeZone='UTC'")
                conn.execute("ATTACH '"+case[other+'_database'].replace("'", "''")+"' AS other_side (READ_ONLY)")
                catalog = conn.execute('SELECT current_database()').fetchone()[0]
                for row in selected:
                    name = row['raw_table'][4:]
                    left = quote(catalog)+'.raw.'+quote(name)
                    right = 'other_side.raw.'+quote(name)
                    sql = 'SELECT (SELECT count(*) FROM (SELECT * FROM '+left+' EXCEPT ALL SELECT * FROM '+right+')),(SELECT count(*) FROM (SELECT * FROM '+right+' EXCEPT ALL SELECT * FROM '+left+'))'
                    counts = conn.execute(sql).fetchone()
                    equal = counts == (0, 0)
                    assert equal == row['sorted_content_hash_equal'], (task, other, name, counts)
                    independent_content.append({'task': task, 'comparison': row['comparison'], 'raw_table': row['raw_table'],
                                                'sql': sql, 'method': 'native SQL EXCEPT ALL', 'gold_only_rows': counts[0], 'other_only_rows': counts[1],
                                                'agrees_with_sorted_hash': True})
        print('Validated inventory and independent content', task, flush=True)

    # Rebuild reachability independently from original B7 and 013 state rows.
    original_scan = read_jsonl(RECORDS/'008_table_scan.jsonl')
    states = read_jsonl(RECORDS/'013_statuses.jsonl')
    state_map = {(r['task'], r['layer'].lower()+'.'+r['table'].lower()): r['status'] for r in states}
    graph = defaultdict(set)
    for row in original_scan:
        for source in row['source_comparison']['agent_direct_read_sources']:
            graph[(row['task'], source.lower())].add(row['layer'].lower()+'.'+row['table'].lower())
    downs = read_jsonl(RECORDS/'015_pending_downstream.jsonl')
    differences = {(r['task'], r['raw_table']) for r in rows if r['comparison_applicable'] and r['different']}
    assert differences == {(r['task'], r['raw_table']) for r in downs}
    target_union = set()
    for row in downs:
        task, start = row['task'], row['raw_table']
        seen, todo = {start}, deque([start])
        while todo:
            for target in graph[(task, todo.popleft())]:
                if target not in seen:
                    todo.append(target)
                    seen.add(target)
        expected = {n for n in seen if state_map.get((task, n)) == '待标注'}
        actual = {t['layer'].lower()+'.'+t['table'].lower() for t in row['pending_downstream_tables']}
        assert expected == actual, (task, start)
        for target in row['pending_downstream_tables']:
            path = target['one_shortest_path']
            assert path[0] == start
            assert path[-1] == target['layer'].lower()+'.'+target['table'].lower()
            assert len(path)-1 == target['hops']
            for left, right in zip(path, path[1:]):
                assert right in graph[(task, left)]
            target_union.add((task, path[-1]))
    summary = json.loads((RECORDS/'015_summary.json').read_text())
    assert len(target_union) == summary['pending_downstream_table_count']
    assert not summary['lineage_limit_records']
    assert not any(r['incomplete_read'] for r in rows)
    assert len(states) == 1069 and Counter(r['status'] for r in states)['待标注'] == 283

    before = json.loads((RECORDS/'015_input_before.json').read_text())
    changes = []
    database_files = 0
    for name, old in before['files'].items():
        path = Path(name)
        new = fingerprint(path) if path.is_file() else None
        if path.suffix in ('.duckdb', '.db'):
            database_files += 1
        if old != new:
            changes.append({'path': name, 'before': old, 'after': new})
    integrity = {'checked_at': stamp(), 'compared_fields': ['bytes', 'mtime_ns', 'sha256'],
                 'files_checked': len(before['files']), 'database_files_checked': database_files,
                 'unchanged': not changes, 'changes': changes}
    save(RECORDS/'015_input_integrity.json', integrity)
    assert not changes, changes
    tracked = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD'], cwd=ROOT, text=True).splitlines()
    assert not any(re.match(r'(?:records|notes)/(?:00[4-9]|01[0-4])', path) for path in tracked), tracked
    validation = {'passed': True, 'checked_at': stamp(), 'cases': len(cases), 'comparison_rows': len(rows),
                  'raw_side_table_inventories_rechecked': inventory_tables,
                  'content_hash_streams': hash_streams, 'content_hash_rows': hash_rows,
                  'independent_multiset_checks': independent_content,
                  'original_files': integrity, 'prior_004_014_unchanged': True,
                  'downstream_raw_entries': len(downs), 'pending_downstream_tables': len(target_union),
                  'source_status_counts': dict(Counter(r['status'] for r in states))}
    save(RECORDS/'015_validation.json', validation)
    report = ROOT/'notes/015_2026-10-29_gold原始表一致性检查.md'
    links = []
    for dest in re.findall(r'\]\(([^)]+)\)', report.read_text()):
        if '://' not in dest:
            target = report.parent/dest
            assert target.is_file(), str(target)
            links.append(dest)
    validation['local_report_links_verified'] = len(links)
    save(RECORDS/'015_validation.json', validation)
    print('PASS', len(rows), 'comparison rows;', len(independent_content), 'independent multiset checks;', len(before['files']), 'files and', database_files, 'databases unchanged;', len(links), 'report links', flush=True)


if __name__ == '__main__':
    main()
