"""Explicitly repair a discovered snapshot gap without backdating the original audit.

Historical derived retained databases were not in the first manifest. Snapshot
them now, re-read every affected retained comparison, and fingerprint again.
This proves this revalidation's immutability, not the earlier read's history.
"""
from annotate_dacomp_batch023 import *
from fingerprint_dacomp_batch023 import fp

initial = json.loads((REC/'023_input_before.json').read_text())['files']
affected = []
for path in sorted(REC.glob('023_*reruns_*.json')):
    data = json.loads(path.read_text())
    if data['basis']['prediction_database'] not in initial:
        affected.append((path, data))
paths = sorted({x['basis']['prediction_database'] for _, x in affected})
start = datetime.datetime.now(datetime.timezone.utc).isoformat()
before = dict(started_utc=start, files={p: fp(Path(p)) for p in paths},
              completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              purpose='发现历史派生库未进首次快照；本快照仅用于其后的留存差异重查，不追溯冒充首次快照')
save(REC/'023_derived_input_before.json', before)
work = ROOT/'data/023_diagnostics/derived_recheck.duckdb'
checks = []; cache = {}
for path, data in affected:
    b = data['basis']; key = (b['prediction_database'], b['gold_database'], b['actual_schema'], b['table'])
    if key not in cache:
        with duckdb.connect(str(work)) as c:
            c.execute("SET threads=2; SET memory_limit='1500MB'")
            c.create_function('tolerance_forms',udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}))
            c.execute(f"ATTACH '{b['prediction_database']}' AS retained (READ_ONLY)")
            c.execute(f"ATTACH '{b['gold_database']}' AS gold (READ_ONLY)")
            rel=b['actual_schema']+'.'+b['table']
            cache[key] = compare_sql(c,'retained.'+rel,'gold.'+rel,b)
    result = cache[key]
    assert result == data['retained'], path
    checks.append(dict(record=str(path.relative_to(ROOT)), task=data['task'], table=b['table'],
                       reread_matches_previously_recorded=True, comparison=result))
    save(REC/'023_derived_recheck.json',dict(started_utc=start, checks=checks))
    print(b['table'], 'same retained comparison', flush=True)
after = dict(completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
             files={p: fp(Path(p)) for p in paths})
after['changes']=[p for p in paths if before['files'][p]!=after['files'][p]]
assert not after['changes']
save(REC/'023_derived_input_after.json',after)
save(REC/'023_derived_recheck.json',dict(started_utc=start,
     completed_utc=after['completed_utc'], snapshot_gap_disclosed=True,
     databases=len(paths), independent_comparisons=len(cache), checks=checks,
     limitations='未能追溯证明这些派生库首次读取前的不变性；补采快照后的所有留存对比已重新读取并核实一致。'))
print('rechecked',len(paths),'databases',len(cache),'comparisons',len(checks),'records',flush=True)
