"""Task 015: read-only gold/initial/agent raw inventories, hashes and B7 lineage."""

from collections import Counter, defaultdict, deque
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import uuid

from check_dacomp_constraints import open_readonly, raw_dependency
from compare_dacomp_staging import fingerprint, quote
from complete_dacomp_comparisons import ROOT, RECORDS, save, stamp

PREFIX = '015'


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_jsonl(path, rows):
    path.write_text(''.join(json.dumps(r, ensure_ascii=False, separators=(',', ':'))+'\n' for r in rows))


def cases():
    result = []
    for old in json.loads((RECORDS/'013_cases.json').read_text()):
        case = {k: old[k] for k in ('task', 'initial_database', 'agent_database', 'initial_directory')}
        case['gold_database'] = json.loads((RECORDS/f"006_contract_{case['task']}.json").read_text())['gold_database']
        case['gold_directory'] = str(Path(case['gold_database']).parent)
        result.append(case)
    return result


def prepare():
    target = RECORDS/'015_input_before.json'
    if target.exists():
        raise RuntimeError('Existing 015 input baseline must not be replaced')
    inputs = cases()
    paths = set(json.loads((RECORDS/'014_input_before.json').read_text())['files'])
    for base in (ROOT/'records', ROOT/'notes'):
        for path in base.rglob('*'):
            relative = path.relative_to(base)
            if path.is_file() and relative.parts[0][:3].isdigit() and 4 <= int(relative.parts[0][:3]) <= 14:
                paths.add(str(path))
    # Record benchmark file paths without attributing provenance. Include their bytes
    # in the read-only baseline even when only their paths will be reported.
    inventory = []
    for case in inputs:
        for side in ('initial', 'gold'):
            directory = Path(case[f'{side}_directory'])
            for path in sorted(directory.rglob('*')):
                if path.is_file() and not any(x in ('.git', '__pycache__', '.venv') for x in path.relative_to(directory).parts):
                    inventory.append({'task': case['task'], 'directory_side': side, 'path': str(path), 'suffix': path.suffix.lower(), 'bytes': path.stat().st_size})
                    paths.add(str(path))
        for side in ('initial', 'gold', 'agent'):
            path = Path(case[f'{side}_database'])
            paths.add(str(path))
            dependency = path.with_name(path.stem+'_start.duckdb')
            if dependency.is_file():
                paths.add(str(dependency))
    save(RECORDS/'015_cases.json', inputs)
    save(RECORDS/'015_benchmark_file_paths.json', inventory)
    print('Fingerprinting', len(paths), 'inputs', flush=True)
    save(target, {'started_at': stamp(), 'files': {p: fingerprint(Path(p)) for p in sorted(paths)}})
    print('Prepared', len(inputs), 'cases', flush=True)


def inventory(path, scratch):
    scratch.mkdir(parents=True, exist_ok=True)
    with open_readonly(Path(path), scratch) as conn:
        conn.execute("SET TimeZone='UTC'")
        exists = bool(conn.execute("SELECT count(*) FROM information_schema.schemata WHERE catalog_name=current_database() AND schema_name='raw'").fetchone()[0])
        relations = conn.execute("SELECT table_name,table_type FROM information_schema.tables WHERE table_catalog=current_database() AND table_schema='raw' ORDER BY table_name").fetchall()
        tables = {}
        for name, kind in relations:
            columns = conn.execute("SELECT column_name,data_type,ordinal_position FROM information_schema.columns WHERE table_catalog=current_database() AND table_schema='raw' AND table_name=? ORDER BY ordinal_position", [name]).fetchall()
            count_sql = 'SELECT count(*) FROM raw.'+quote(name)
            try:
                count = conn.execute(count_sql).fetchone()[0]
                error = None
            except Exception as exc:
                count, error = None, str(exc)
            tables[name] = {'table_type': kind, 'row_count': count,
                            'columns': [{'name': n, 'type': t, 'ordinal_position': i} for n, t, i in columns],
                            'count_sql': count_sql, 'read_error': error, 'content_hash': None}
        dependency = raw_dependency(Path(path))
        return {'database': str(path), 'raw_schema_exists': exists, 'attached_read_only_source': str(dependency) if dependency else None, 'tables': tables}


def scalar(value):
    """Lossless tagged Python representations for the raw types observed here.

    Names and declared SQL types are compared separately. NULL and empty string
    have different tags; values are never stripped, rounded or case-folded.
    """
    if value is None:
        return ['null']
    if isinstance(value, bool):
        return ['bool', value]
    if isinstance(value, int):
        return ['int', str(value)]
    if isinstance(value, float):
        # DuckDB sorts signed zero/NaN as ties. Canonicalize those SQL-equal values
        # so physical order inside an equal-key block cannot alter the digest.
        return ['float', 'nan' if math.isnan(value) else (0.0 if value == 0 else value).hex()]
    if isinstance(value, Decimal):
        return ['decimal', str(value)]
    if isinstance(value, str):
        return ['str', value]
    if isinstance(value, bytes):
        return ['bytes', value.hex()]
    if isinstance(value, datetime):
        return ['datetime', (value.astimezone(timezone.utc) if value.tzinfo else value).isoformat()]
    if isinstance(value, (date, time)):
        return [type(value).__name__, value.isoformat()]
    if isinstance(value, timedelta):
        return ['timedelta', value.days, value.seconds, value.microseconds]
    if isinstance(value, uuid.UUID):
        return ['uuid', str(value)]
    if isinstance(value, (list, tuple)):
        return ['list', [scalar(v) for v in value]]
    if isinstance(value, dict):
        return ['dict', [[scalar(k), scalar(v)] for k, v in value.items()]]
    raise TypeError('Unsupported value type: '+str(type(value)))


def sorted_hash(conn, table, column_names=None):
    projection = ','.join(quote(x) for x in column_names) if column_names else '*'
    sql = 'SELECT '+projection+' FROM raw.'+quote(table)+' ORDER BY ALL NULLS FIRST'
    digest = hashlib.sha256(b'015_raw_sorted_typed_rows_v1\x00')
    cursor = conn.execute(sql)
    count = 0
    python_types = Counter()
    while batch := cursor.fetchmany(2048):
        for row in batch:
            python_types.update(type(v).__name__ for v in row)
            encoded = json.dumps([scalar(v) for v in row], ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')
            digest.update(len(encoded).to_bytes(8, 'big'))
            digest.update(encoded)
            count += 1
    return {'algorithm': 'SHA-256', 'serialization': '015_raw_sorted_typed_rows_v1', 'sql': sql,
            'rows_hashed': count, 'sha256': digest.hexdigest(), 'python_value_types': dict(python_types),
            'column_order': column_names or 'physical ordinal order', 'read_error': None}


def hash_tables(side, names, scratch):
    if not names:
        return
    with open_readonly(Path(side['database']), scratch) as conn:
        conn.execute("SET TimeZone='UTC'")
        for name in sorted(names):
            try:
                result = sorted_hash(conn, name)
                assert result['rows_hashed'] == side['tables'][name]['row_count']
                side['tables'][name]['content_hash'] = result
            except Exception as exc:
                side['tables'][name]['content_hash'] = {'sha256': None, 'read_error': str(exc)}


def pair(task, other_side, gold, other):
    rows = []
    for name in sorted(set(gold['tables']) | set(other['tables'])):
        a, b = gold['tables'].get(name), other['tables'].get(name)
        ac = {c['name']: c for c in a['columns']} if a else {}
        bc = {c['name']: c for c in b['columns']} if b else {}
        counts_known = bool(a and b and a['row_count'] is not None and b['row_count'] is not None)
        equal_counts = (a['row_count'] == b['row_count']) if counts_known else None
        hashes = [x['content_hash'] for x in (a, b)] if a and b else []
        hashed = bool(equal_counts and all(h and h.get('sha256') for h in hashes))
        equal_hashes = hashes[0]['sha256'] == hashes[1]['sha256'] if hashed else None
        reasons = []
        if a is None: reasons.append('gold_missing_table')
        if b is None: reasons.append(other_side+'_missing_table')
        if a and b:
            if a['columns'] != b['columns']: reasons.append('ordered_columns_or_types_differ')
            if equal_counts is False: reasons.append('row_counts_differ')
            if equal_hashes is False: reasons.append('sorted_content_hash_differ')
        unknown = bool(a and b and (not counts_known or (equal_counts and not hashed)))
        rows.append({'task': task, 'comparison': 'gold_vs_'+other_side, 'raw_table': 'raw.'+name,
                     'gold_raw_schema_exists': gold['raw_schema_exists'], other_side+'_raw_schema_exists': other['raw_schema_exists'],
                     'gold_exists': a is not None, other_side+'_exists': b is not None,
                     'gold': a, other_side: b,
                     'gold_only_columns': [c for c in a['columns'] if c['name'] not in bc] if a else [],
                     other_side+'_only_columns': [c for c in b['columns'] if c['name'] not in ac] if b else [],
                     'type_differences': [{'column': n, 'gold_type': ac[n]['type'], other_side+'_type': bc[n]['type']} for n in sorted(ac.keys() & bc.keys()) if ac[n]['type'] != bc[n]['type']],
                     'column_order_differences': [{'column': n, 'gold_position': ac[n]['ordinal_position'], other_side+'_position': bc[n]['ordinal_position']} for n in sorted(ac.keys() & bc.keys()) if ac[n]['ordinal_position'] != bc[n]['ordinal_position']],
                     'ordered_columns_and_types_equal': a['columns'] == b['columns'] if a and b else None,
                     'row_counts_equal': equal_counts, 'sorted_content_hash_equal': equal_hashes,
                     'different': bool(reasons), 'difference_reasons': reasons, 'incomplete_read': unknown,
                     'gold_database': gold['database'], other_side+'_database': other['database'],
                     'comparison_applicable': gold['raw_schema_exists']})
    return rows


def inspect_cases():
    for case in json.loads((RECORDS/'015_cases.json').read_text()):
        task = case['task']
        scratch = ROOT/'data/015_gold_raw'/task
        sides = {side: inventory(case[side+'_database'], scratch/side) for side in ('gold', 'initial', 'agent')}
        # Content hashes are required exactly for common tables with known equal
        # row counts, regardless of whether their schemas also differ.
        selected = defaultdict(set)
        if sides['gold']['raw_schema_exists']:
            for other in ('initial', 'agent'):
                for name in sides['gold']['tables'].keys() & sides[other]['tables'].keys():
                    a, b = sides['gold']['tables'][name], sides[other]['tables'][name]
                    if a['row_count'] is not None and a['row_count'] == b['row_count']:
                        selected['gold'].add(name)
                        selected[other].add(name)
        print(task, 'raw tables', {s: len(v['tables']) for s, v in sides.items()}, 'hashing', {s: len(n) for s, n in selected.items()}, flush=True)
        for side in ('gold', 'initial', 'agent'):
            hash_tables(sides[side], selected[side], scratch/side)
        comparisons = [row for other in ('initial', 'agent') for row in pair(task, other, sides['gold'], sides[other])]
        result = {'task': task, 'checked_at': stamp(), 'sides': sides, 'comparisons': comparisons}
        save(RECORDS/f'015_raw_{task}.json', result)
        print(task, 'different', Counter(row['comparison'] for row in comparisons if row['different'] and row['comparison_applicable']), flush=True)


def graph_for(task, scan, status_rows):
    """Literal B7 names only; no suffix resolution or extra SQL inference."""
    graph = defaultdict(set)
    edges = []
    unresolved = []
    scan_nodes = {r['layer'].lower()+'.'+r['table'].lower() for r in scan}
    for row in scan:
        target = row['layer'].lower()+'.'+row['table'].lower()
        source_info = row['source_comparison']
        if not source_info.get('complete'):
            unresolved.append({'target': target, 'reason': '008_source_scan_incomplete'})
        for source in source_info['agent_direct_read_sources']:
            source_key = source.lower()
            graph[source_key].add(target)
            edges.append({'task': task, 'source': source_key, 'target': target,
                          'original_008_source': source, 'source_record': 'records/008_table_scan.jsonl'})
            if not source_key.startswith('raw.') and source_key not in scan_nodes:
                unresolved.append({'target': target, 'source': source, 'reason': '008_source_has_no_exact_schema_qualified_output_node'})
    pending = {r['layer'].lower()+'.'+r['table'].lower(): r for r in status_rows if r['task'] == task and r['status'] == '待标注'}
    return graph, pending, edges, unresolved


def descendants(graph, start, pending):
    paths = {start: [start]}
    todo = deque([start])
    while todo:
        source = todo.popleft()
        for target in sorted(graph.get(source, ())):
            if target not in paths:
                paths[target] = paths[source]+[target]
                todo.append(target)
    return [{'task': pending[n]['task'], 'layer': pending[n]['layer'], 'table': pending[n]['table'],
             'status_013': '待标注', 'status_source': 'records/013_statuses.jsonl',
             'direct': len(paths[n]) == 2, 'hops': len(paths[n])-1, 'one_shortest_path': paths[n],
             'direct_upstream_nodes_within_reachable_graph': sorted(s for s, ts in graph.items() if n in ts and s in paths)}
            for n in sorted(set(paths) & set(pending))]


def finalize_records():
    states = read_jsonl(RECORDS/'013_statuses.jsonl')
    scans = read_jsonl(RECORDS/'008_table_scan.jsonl')
    source_files = json.loads((RECORDS/'015_benchmark_file_paths.json').read_text())
    all_comparisons, summaries, downstream, edges, limitations = [], [], [], [], []
    for case in json.loads((RECORDS/'015_cases.json').read_text()):
        task = case['task']
        doc = json.loads((RECORDS/f'015_raw_{task}.json').read_text())
        applicable = [r for r in doc['comparisons'] if r['comparison_applicable']]
        all_comparisons.extend(doc['comparisons'])
        different_names = sorted({r['raw_table'] for r in applicable if r['different']})
        graph, pending, es, unknown = graph_for(task, [r for r in scans if r['task'] == task], states)
        edges.extend(es)
        limitations.extend({'task': task, **r} for r in unknown)
        for name in different_names:
            downstream.append({'task': task, 'raw_table': name,
                               'different_in': [r['comparison'] for r in applicable if r['raw_table'] == name and r['different']],
                               'source_record': f'records/015_raw_{task}.json',
                               'lineage_source': 'records/008_table_scan.jsonl: source_comparison.agent_direct_read_sources',
                               'pending_downstream_tables': descendants(graph, name, pending)})
        suffixes = {'.duckdb', '.db', '.csv', '.tsv', '.parquet', '.json', '.jsonl', '.xlsx', '.xls', '.sqlite', '.sqlite3', '.zip', '.gz'}
        candidates = [r for r in source_files if r['task'] == task and r['suffix'] in suffixes]
        summary = {'task': task, 'gold_raw_schema_exists': doc['sides']['gold']['raw_schema_exists'],
                   'raw_table_counts': {s: len(v['tables']) for s, v in doc['sides'].items()},
                   'distinct_different_raw_tables': len(different_names),
                   'different_raw_tables': different_names,
                   'candidate_benchmark_files_when_gold_raw_absent': candidates if not doc['sides']['gold']['raw_schema_exists'] else [],
                   'candidate_provenance': 'Paths only: generation-time use is not established',
                   'pending_downstream_union': sorted({t['layer']+'.'+t['table'] for r in downstream if r['task'] == task for t in r['pending_downstream_tables']})}
        for other in ('initial', 'agent'):
            rows = [r for r in applicable if r['comparison'] == 'gold_vs_'+other]
            summary['gold_vs_'+other] = {'union_tables': len(rows), 'different_tables': sum(r['different'] for r in rows),
                'equal_tables': sum(not r['different'] and not r['incomplete_read'] for r in rows),
                'gold_only_tables': [r['raw_table'] for r in rows if r['gold_exists'] and not r[other+'_exists']],
                other+'_only_tables': [r['raw_table'] for r in rows if not r['gold_exists'] and r[other+'_exists']],
                'schema_different_tables': sum(r['ordered_columns_and_types_equal'] is False for r in rows),
                'row_count_different_tables': sum(r['row_counts_equal'] is False for r in rows),
                'content_hash_checked_tables': sum(r['sorted_content_hash_equal'] is not None for r in rows),
                'content_hash_different_tables': sum(r['sorted_content_hash_equal'] is False for r in rows),
                'incomplete_reads': sum(r['incomplete_read'] for r in rows)}
        summaries.append(summary)
    write_jsonl(RECORDS/'015_raw_comparisons.jsonl', all_comparisons)
    write_jsonl(RECORDS/'015_pending_downstream.jsonl', downstream)
    write_jsonl(RECORDS/'015_lineage_edges.jsonl', edges)
    save(RECORDS/'015_lineage_limits.json', limitations)
    save(RECORDS/'015_summary.json', {'tasks': summaries, 'gold_raw_present_tasks': sum(r['gold_raw_schema_exists'] for r in summaries),
        'gold_raw_absent_tasks': [r['task'] for r in summaries if not r['gold_raw_schema_exists']],
        'different_raw_tables': len(downstream), 'tasks_with_raw_differences': sum(bool(r['distinct_different_raw_tables']) for r in summaries),
        'pending_downstream_table_count': len({(r['task'], t['layer'], t['table']) for r in downstream for t in r['pending_downstream_tables']}),
        'lineage_edges': len(edges), 'lineage_limit_records': len(limitations),
        'comparison_totals': {other: {k: sum(r['gold_vs_'+other][k] for r in summaries) for k in ('union_tables', 'different_tables', 'equal_tables', 'schema_different_tables', 'row_count_different_tables', 'content_hash_checked_tables', 'content_hash_different_tables', 'incomplete_reads')} for other in ('initial', 'agent')}})
    flat = []
    for r in all_comparisons:
        other = r['comparison'].removeprefix('gold_vs_')
        a, b = r['gold'], r[other]
        flat.append({k: r[k] for k in ('task', 'comparison', 'raw_table', 'comparison_applicable', 'different', 'incomplete_read', 'ordered_columns_and_types_equal', 'row_counts_equal', 'sorted_content_hash_equal')} | {
            'gold_rows': a['row_count'] if a else None, other+'_rows': b['row_count'] if b else None,
            'gold_hash': (a['content_hash'] or {}).get('sha256') if a else None,
            'other_hash': (b['content_hash'] or {}).get('sha256') if b else None,
            'difference_reasons': ';'.join(r['difference_reasons'])})
    # One shared CSV has fixed side-neutral column labels.
    for r in flat:
        r['other_rows'] = r.pop('initial_rows', r.pop('agent_rows', None))
    with (RECORDS/'015_raw_comparisons.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(flat[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(flat)
    print('Final summary', json.dumps(json.loads((RECORDS/'015_summary.json').read_text()) | {'tasks': '(30 task rows)'}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    {'prepare': prepare, 'inspect': inspect_cases, 'summarize': finalize_records}[sys.argv[1]]()
