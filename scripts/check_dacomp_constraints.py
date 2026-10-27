"""Check explicitly declared DAComp constraints on retained prediction/gold, read-only."""

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys
import time

import duckdb
import yaml
from yaml.nodes import MappingNode, SequenceNode

from compare_dacomp_staging import fingerprint, plain, quote

ROOT = Path(__file__).resolve().parents[1]
PROJECT = Path("/home/katherine/dac")
CONFIG = PROJECT / "benchmarks/DAComp-code/dacomp-de/evaluation_suite/evaluation_config_compare.yaml"
PYTHON = PROJECT / ".venv-openhands/bin/python"
KINDS = ("grain", "primary_key", "not_null", "unique")
POLICY = "006_explicit_constraints_v1"
IDENTIFIER = r'(?:`[^`]+`|"[^"]+"|[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)?)'
SEPARATOR = re.compile(r"(?:\s*,\s*(?:and\s+)?|\s+(?:and|per|x)\s+|\s*[+×]\s*)", re.I)
REPETITION = re.compile(r"\b(?:duplicates?|duplicated|duplication|repeats?|repeated|multiple|multiply|multiplied|occurrences?|one or more|no enforced uniqueness|no de-duplication|source records?|source rows?|input records?|input rows?|row-for-row|each matching)\b", re.I)


def save(path, value):
    temporary = path.with_suffix(path.suffix + ".pending")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


def grain_columns(text, columns):
    if text is None:
        return {"status": "not_declared", "columns": []}
    raw = str(text).strip()
    if REPETITION.search(raw):
        return {"status": "unparsed", "reason": "repetition_or_source_record_grain_is_explicit", "columns": []}
    prefix = re.match(r"^One (?:validated )?row per\s+", raw, re.I)
    if not prefix:
        return {"status": "unparsed", "reason": "not_a_supported_one_row_per_column_statement", "columns": []}
    body = raw[prefix.end():]
    modifier = re.match(r"(?:(?:unique|distinct|exact) combination of |combination of |distinct |non-null |active )", body, re.I)
    if modifier:
        body = body[modifier.end():]
    parenthesized = body.startswith("(")
    suffix = ""
    if parenthesized:
        close = body.find(")")
        if close < 0:
            return {"status": "unparsed", "reason": "unclosed_column_list", "columns": []}
        suffix, body = body[close + 1:].strip(), body[1:close].strip()
    names, consumed, bad = [], 0, []
    available = {c.lower(): c for c in columns}
    while True:
        token = re.match(IDENTIFIER, body[consumed:])
        if not token:
            return {"status": "unparsed", "reason": "column_list_has_unresolved_tokens", "columns": [], "unresolved_text": body[consumed:]}
        identifier = token.group()
        name = identifier[1:-1] if identifier.startswith(('`', '"')) else identifier.split('.')[-1]
        if name.lower() not in available:
            bad.append(name)
        names.append(available.get(name.lower(), name))
        consumed += token.end()
        separator = SEPARATOR.match(body, consumed)
        if not separator:
            annotation = re.match(r"\s*\([^()]*\)", body[consumed:])
            if annotation:
                after_annotation = consumed + annotation.end()
                following = SEPARATOR.match(body, after_annotation)
                if following:
                    separator = following
        if not separator:
            break
        consumed = separator.end()
    tail = (body[consumed:].strip() + " " + suffix).strip()
    if bad:
        return {"status": "unparsed", "reason": "identifiers_not_declared_as_contract_columns", "columns": [], "unresolved_identifiers": bad}
    # Qualifiers may restrict the declared rows; no new grain dimensions are inferred.
    simple_tail = not tail or tail == '.' or re.fullmatch(r"(?:pair|combination)\.?", tail, re.I)
    qualifier_tail = re.match(r"^(?:with\b|where\b|present in\b|from\b|in\b|within\b|for\b|that exists\b)", tail, re.I)
    annotation_tail = re.fullmatch(r"\([^();]*\)(?:\s+(?:with|for|from|where)\b[^;]*)?\.?", tail, re.I)
    if not (simple_tail or qualifier_tail or annotation_tail) or ';' in tail or re.search(r'\bper\b', tail, re.I):
        return {"status": "unparsed", "reason": "unresolved_grain_qualifier_or_additional_dimension", "columns": [], "unresolved_text": tail}
    if len(set(names)) != len(names):
        return {"status": "unparsed", "reason": "repeated_column_in_grain_list", "columns": []}
    return {"status": "parsed", "columns": names, "qualifier_original": tail,
            "policy": "explicit identifiers matched to contract columns; no synonyms or inferred IDs"}


def fields(node):
    return {key.value: value for key, value in node.value} if isinstance(node, MappingNode) else {}


def extract_contract(path):
    path = Path(path)
    text = path.read_text()
    try:
        root = yaml.compose(text)
        mode, error = "strict", None
    except yaml.YAMLError as original_error:
        root = yaml.compose(text.replace("\\", "\\\\"))
        mode, error = "escape_backslashes_in_memory_for_structure_only", str(original_error)
    lines = text.splitlines(keepends=True)

    def reference(key, value, trail):
        start = key.start_mark.line
        end = min(len(lines), value.end_mark.line + (1 if value.end_mark.column else 0))
        return {"yaml_path": trail, "start_line": start + 1, "end_line": end,
                "original_excerpt": ''.join(lines[start:end]), "decoded_value": plain(value)}

    root_fields = fields(root)
    staging = fields(root_fields["staging_contract"])["tables"]
    modeling = root_fields["modeling_spec"]
    groups = [("staging", staging, ["staging_contract", "tables"])]
    groups += [(k.value.removesuffix("_models"), v, ["modeling_spec", k.value]) for k,v in modeling.value if k.value.endswith("_models")]
    tables = []
    for layer, collection, trail in groups:
        values = [(i, n) for i,n in enumerate(collection.value)] if isinstance(collection, SequenceNode) else [(k.value,v) for k,v in collection.value]
        for index, node in values:
            mapping = fields(node)
            spec = plain(node)
            name = spec.get("name", index)
            if not isinstance(name, str):
                raise ValueError(f"A contract table has no explicit name: {path} {trail} {index}")
            table_path = trail + [index]
            columns_node = mapping.get("columns")
            column_nodes = [(i,n) for i,n in enumerate(columns_node.value)] if isinstance(columns_node, SequenceNode) else [(k.value,v) for k,v in columns_node.value]
            columns = []
            declarations = {k: [] for k in KINDS}
            ignored = []
            for column_index, column_node in column_nodes:
                column_fields = fields(column_node)
                column = plain(column_node)
                column_name = column.get("name", column_index)
                columns.append(column_name)
                for key_node, value in column_node.value:
                    if key_node.value not in ("constraints", "tests"):
                        continue
                    entries = value.value if isinstance(value, SequenceNode) else [value]
                    for entry_index, entry in enumerate(entries):
                        decoded = plain(entry)
                        kind = decoded.strip().lower().replace(' ', '_') if isinstance(decoded, str) else None
                        source = reference(key_node, value, table_path + ["columns", column_index, key_node.value, entry_index])
                        if kind in ("not_null", "unique", "primary_key"):
                            existing = next((d for d in declarations[kind] if d["columns"] == [column_name]), None)
                            if existing:
                                existing["sources"].append(source)
                            else:
                                declarations[kind].append({"columns": [column_name], "sources": [source]})
                        else:
                            ignored.append({"column": column_name, "field": key_node.value, "value": decoded})
            for key_node, value in node.value:
                if key_node.value in ("primary_key", "primary_keys"):
                    key_columns = plain(value)
                    if isinstance(key_columns, str):
                        key_columns = [key_columns]
                    if not isinstance(key_columns, list) or not key_columns or not all(isinstance(x,str) for x in key_columns):
                        raise ValueError(f"Unsupported explicit primary key at {path}: {table_path}")
                    declarations["primary_key"].append({"columns": key_columns, "sources": [reference(key_node,value,table_path+[key_node.value])]})
                if key_node.value == "grain":
                    raw_grain = plain(value)
                    parsed = grain_columns(raw_grain, columns)
                    declarations["grain"].append({"raw_text": raw_grain, **parsed,
                                                   "sources": [reference(key_node,value,table_path+["grain"])]})
            tables.append({"layer": layer, "table": name, "contract_yaml_path": table_path,
                           "contract_start_line": node.start_mark.line + 1, "declared_columns": columns,
                           "declarations": declarations, "other_declared_tests_not_executed": ignored})
    merged = {}
    for table in tables:
        key = (table['layer'],table['table'])
        definition = {k:table[k] for k in ('contract_yaml_path','contract_start_line','declared_columns')}
        if key not in merged:
            merged[key] = {**table,'definitions':[definition]}
            continue
        target = merged[key]
        target['definitions'].append(definition)
        target['declared_columns'] = list(dict.fromkeys(target['declared_columns']+table['declared_columns']))
        for kind in KINDS:
            for declaration in table['declarations'][kind]:
                existing = next((d for d in target['declarations'][kind] if d['columns']==declaration['columns'] and (kind!='grain' or d['raw_text']==declaration['raw_text'] and d['status']==declaration['status'])),None)
                if existing:existing['sources'].extend(declaration['sources'])
                else:target['declarations'][kind].append(declaration)
        target['other_declared_tests_not_executed'].extend(table['other_declared_tests_not_executed'])
    return {"path": str(path), "sha256": fingerprint(path)["sha256"], "parse_mode": mode,
            "original_yaml_parse_error": error, "table_definition_entries": len(tables),
            "duplicate_definitions": [{'layer':t['layer'],'table':t['table'],'definitions':t['definitions']} for t in merged.values() if len(t['definitions'])>1],
            "tables": list(merged.values())}


def raw_dependency(path):
    with duckdb.connect(str(path), read_only=True) as conn:
        views = conn.execute("SELECT sql FROM duckdb_views() WHERE schema_name='raw'").fetchall()
    if not any(re.search(r'\bFROM\s+"?source"?\.raw\.', sql, re.I) for (sql,) in views):
        return None
    source = path.with_name(path.stem + "_start.duckdb")
    return source if source.is_file() else None


def open_readonly(path, scratch):
    conn = duckdb.connect(str(path), read_only=True)
    conn.execute("SET memory_limit='512MB'; SET threads=2")
    conn.execute("SET temp_directory='" + str(scratch).replace("'", "''") + "'")
    dependency = raw_dependency(path)
    if dependency:
        conn.execute("ATTACH '" + str(dependency).replace("'", "''") + "' AS source (READ_ONLY)")
    return conn


def category_summary(items):
    if not items:
        return {"status": "not_declared", "violated": None, "declared_checks": 0, "checked_checks": 0, "unknown_checks": 0}
    checked = sum(x["status"] == "checked" for x in items)
    violations = any(x.get("violated") is True for x in items)
    complete = checked == len(items)
    return {"status": "violated" if violations else "checked_no_violation" if complete else "unknown",
            "violated": True if violations else False if complete else None,
            "declared_checks": len(items), "checked_checks": checked, "unknown_checks": len(items)-checked,
            "complete": complete}


def inspect_table(conn, entry):
    table, layer = entry["table"], entry["layer"]
    schemas = [layer] + (["mart"] if layer == "marts" else ["marts"] if layer == "mart" else [])
    locations = conn.execute("SELECT table_schema,table_name,table_type FROM information_schema.tables WHERE table_catalog=current_database() AND lower(table_name)=lower(?)", [table]).fetchall()
    selected = next((row for s in schemas for row in locations if row[0].lower() == s.lower()), None)
    output = {"table_exists": selected is not None, "actual_schema": selected[0] if selected else None,
              "table_type": selected[2] if selected else None, "same_name_other_schemas": [r[0] for r in locations if r[0] not in schemas],
              "row_count": None, "checks": {k: [] for k in KINDS}}
    columns = []
    relation = None
    if selected:
        relation = quote(selected[0]) + '.' + quote(selected[1])
        output["actual_table"] = selected[1]
        columns = [r[0] for r in conn.execute("SELECT column_name FROM information_schema.columns WHERE table_catalog=current_database() AND table_schema=? AND table_name=? ORDER BY ordinal_position",[selected[0],selected[1]]).fetchall()]
        try:
            output["row_count"] = conn.execute("SELECT count(*) FROM " + relation).fetchone()[0]
        except Exception as error:
            output["row_count_error"] = {"type": type(error).__name__, "message": str(error)}
    mapping = {c.lower():c for c in columns}
    output["actual_columns"] = columns
    output["missing_declared_columns"] = [c for c in entry["declared_columns"] if c.lower() not in mapping] if selected else None
    nulls, null_error = {}, None
    needed_nulls = sorted({d["columns"][0] for d in entry["declarations"]["not_null"] if d["columns"][0].lower() in mapping})
    if selected and needed_nulls:
        sql = 'SELECT ' + ','.join(f"count(*) FILTER(WHERE {quote(mapping[c.lower()])} IS NULL)" for c in needed_nulls) + ' FROM ' + relation
        try:
            nulls = dict(zip(needed_nulls, conn.execute(sql).fetchone()))
            output["not_null_count_sql"] = sql
        except Exception as error:
            null_error = {"type": type(error).__name__, "message": str(error)}
    cache = {}
    for kind in KINDS:
        for declaration in entry["declarations"][kind]:
            result = {"columns": declaration["columns"], "status": "unknown", "violated": None}
            if not selected:
                result.update(status="table_missing")
            elif kind == "grain" and declaration["status"] != "parsed":
                result.update(status="grain_unparsed", reason=declaration.get("reason"))
            elif any(c.lower() not in mapping for c in declaration["columns"]):
                result.update(status="columns_missing", missing_columns=[c for c in declaration["columns"] if c.lower() not in mapping])
            elif kind == "not_null":
                name = declaration["columns"][0]
                if null_error:
                    result.update(status="query_error", error=null_error)
                else:
                    result.update(status="checked", sql_null_rows=nulls[name], violated=nulls[name] > 0)
            else:
                key = tuple(sorted({mapping[c.lower()] for c in declaration["columns"]}))
                if key not in cache:
                    key_sql = ','.join(quote(c) for c in key)
                    any_null = ' OR '.join(quote(c)+' IS NULL' for c in key)
                    alias = '__ledger_group_count'
                    while alias.lower() in mapping: alias += '_'
                    frequency = quote(alias)
                    sql = f"""SELECT count(*),count(*) FILTER(WHERE {frequency}>1),coalesce(sum({frequency}) FILTER(WHERE {frequency}>1),0),
                      coalesce(sum({frequency}-1) FILTER(WHERE {frequency}>1),0),coalesce(sum({frequency}) FILTER(WHERE {any_null}),0),
                      count(*) FILTER(WHERE {frequency}>1 AND NOT ({any_null})),coalesce(sum({frequency}) FILTER(WHERE {frequency}>1 AND NOT ({any_null})),0),
                      coalesce(sum({frequency}-1) FILTER(WHERE {frequency}>1 AND NOT ({any_null})),0),count(*) FILTER(WHERE {frequency}>1 AND ({any_null})),
                      coalesce(sum({frequency}) FILTER(WHERE {frequency}>1 AND ({any_null})),0)
                      FROM (SELECT {key_sql},count(*) AS {frequency} FROM {relation} GROUP BY {key_sql}) grouped_keys"""
                    try:
                        row = conn.execute(sql).fetchone()
                        cache[key] = {"sql": sql, "sql_key_order": list(key), **dict(zip(("distinct_key_groups", "duplicate_key_groups", "rows_in_duplicate_groups", "excess_duplicate_rows", "null_key_rows", "nonnull_duplicate_key_groups", "nonnull_rows_in_duplicate_groups", "nonnull_excess_duplicate_rows", "null_containing_duplicate_key_groups", "rows_in_null_containing_duplicate_groups"),row))}
                    except Exception as error:
                        cache[key] = {"error": {"type": type(error).__name__, "message": str(error)}, "sql": sql}
                profile = cache[key]
                if "error" in profile:
                    result.update(status="query_error", **profile)
                else:
                    result.update(status="checked", **profile)
                    if kind == "unique":
                        result["including_nulls_duplicate_key_groups"] = profile["duplicate_key_groups"]
                        result["including_nulls_rows_in_duplicate_groups"] = profile["rows_in_duplicate_groups"]
                        result["duplicate_key_groups"] = profile["nonnull_duplicate_key_groups"]
                        result["rows_in_duplicate_groups"] = profile["nonnull_rows_in_duplicate_groups"]
                        result["excess_duplicate_rows"] = profile["nonnull_excess_duplicate_rows"]
                    result["violated"] = result["duplicate_key_groups"] > 0 or kind == "primary_key" and profile["null_key_rows"] > 0
            output["checks"][kind].append(result)
    output["categories"] = {k: category_summary(v) for k,v in output["checks"].items()}
    declared = [s for s in output["categories"].values() if s["declared_checks"]]
    output["any_constraint_violated"] = True if any(s["violated"] is True for s in declared) else False if declared and all(s["violated"] is False for s in declared) else None
    return output


def paths(number, configs):
    task, short = f"dacomp-de-impl-{number:03d}", f"impl-{number:03d}"
    db = configs[task]["database_file"]
    return {"task": short, "contract": PROJECT / "benchmarks/dacomp-de" / task / "docs/data_contract.yaml",
            "agent": PROJECT / "runs/20261025_de_official_batch_01" / short / "agent" / task / db,
            "gold": PROJECT / "benchmarks/dacomp-de-gold" / task / db}


def worker(number):
    configs = yaml.safe_load(CONFIG.read_text())["examples"]
    locations = paths(number, configs)
    contract = extract_contract(locations["contract"])
    scratch = ROOT / "data/006_constraint_scratch" / locations["task"]
    scratch.mkdir(parents=True, exist_ok=True)
    result = {"task": locations["task"], "policy": POLICY, "started_at_utc":datetime.now(timezone.utc).isoformat(),
              "contract": {k:v for k,v in contract.items() if k!='tables'},
              "agent_database": str(locations["agent"]), "gold_database": str(locations["gold"]), "tables": []}
    connections = {side: open_readonly(locations[side], scratch / side) for side in ("agent", "gold")}
    try:
        for entry in contract["tables"]:
            record = {"task": locations["task"], **entry,
                      "agent": inspect_table(connections["agent"], entry), "gold": inspect_table(connections["gold"], entry)}
            result["tables"].append(record)
            print(f"{locations['task']} {entry['layer']}.{entry['table']}: agent_exists={record['agent']['table_exists']}, gold_exists={record['gold']['table_exists']}", flush=True)
    finally:
        for conn in connections.values():
            conn.close()
    result['finished_at_utc']=datetime.now(timezone.utc).isoformat()
    save(ROOT / f"records/006_contract_{locations['task']}.json", result)


def summarize(records):
    output = {}
    for kind in (*KINDS, "any"):
        selected = [r for r in records if kind == "any" and any(r["declarations"].values()) or kind != "any" and r["declarations"][kind]]
        def value(row, side):
            return row[side]["any_constraint_violated"] if kind == "any" else row[side]["categories"][kind]["violated"]
        item = {"declared_tables": len(selected)}
        for side in ("agent", "gold"):
            bad = [r for r in selected if value(r,side) is True]
            item[side] = {"violating_tables": len(bad), "violating_tasks": len({r['task'] for r in bad}),
                          "checked_no_violation_tables": sum(value(r,side) is False for r in selected),
                          "unknown_tables": sum(value(r,side) is None for r in selected),
                          "table_missing": sum(not r[side]["table_exists"] for r in selected)}
        both = [r for r in selected if value(r,'agent') is True and value(r,'gold') is True]
        item["both_violating_tables"] = len(both)
        item["both_violating_tasks"] = len({r['task'] for r in both})
        output[kind] = item
    return output


def outputs():
    tasks = [json.loads((ROOT/f"records/006_contract_impl-{n:03d}.json").read_text()) for n in range(1,31)]
    records = [r for t in tasks for r in t["tables"]]
    with (ROOT/"records/006_contract_checks.jsonl").open("w") as stream:
        for record in records:
            stream.write(json.dumps(record,ensure_ascii=False,separators=(',',':'))+'\n')
    rows = []
    for r in records:
        row = {"task": r["task"], "layer": r["layer"], "table": r["table"],
               "grain_original": r["declarations"]["grain"][0]["raw_text"] if r["declarations"]["grain"] else None,
               "grain_parse_status": r["declarations"]["grain"][0]["status"] if r["declarations"]["grain"] else "not_declared",
               "grain_columns": json.dumps([d["columns"] for d in r["declarations"]["grain"]],ensure_ascii=False),
               **{k+"_declared":json.dumps([d["columns"] for d in r["declarations"][k]],ensure_ascii=False) for k in KINDS if k!='grain'}}
        for side in ("agent","gold"):
            row.update({side+"_exists":r[side]["table_exists"],side+"_rows":r[side]["row_count"],side+"_any_violated":r[side]["any_constraint_violated"]})
            for kind in KINDS:
                row[side+'_'+kind+'_violated'] = r[side]["categories"][kind]["violated"]
                row[side+'_'+kind+'_checks'] = json.dumps(r[side]["checks"][kind],ensure_ascii=False,separators=(',',':'))
        rows.append(row)
    with (ROOT/"records/006_contract_checks.csv").open('w',newline='') as stream:
        writer = csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    grain_counts = Counter(r["declarations"]["grain"][0]["status"] if r["declarations"]["grain"] else 'not_declared' for r in records)
    summary = {"policy":POLICY,"created_at_utc":datetime.now(timezone.utc).isoformat(),"python":sys.version.split()[0],"duckdb":duckdb.__version__,
               "tasks":30,"tables":len(records),"table_definition_entries":sum(t['contract']['table_definition_entries'] for t in tasks),
               "duplicate_definitions":[{'task':t['task'],**d} for t in tasks for d in t['contract']['duplicate_definitions']],
               "layers":dict(Counter(r['layer'] for r in records)),"grain_status":dict(grain_counts),
               "summary":summarize(records),"query_errors":[{"task":r['task'],"layer":r['layer'],"table":r['table'],"side":side,"kind":k,"error":c['error']} for r in records for side in ('agent','gold') for k in KINDS for c in r[side]['checks'][k] if c['status']=='query_error'],
               "missing_tables":{s:sum(not r[s]['table_exists'] for r in records) for s in ('agent','gold')},
               "grain_unparsed_reasons":dict(Counter(r['declarations']['grain'][0].get('reason') for r in records if r['declarations']['grain'] and r['declarations']['grain'][0]['status']!='parsed')),
               "normalization":"native typed SQL values; no trim/lower/round/NULL string replacement",
               "unique_null_policy":"exclude keys containing SQL NULL from unique violations; also report duplicate groups including NULL",
               "primary_key_policy":"duplicates including NULL groups, plus any SQL NULL key rows violate primary_key; not_null category only explicit not_null declarations",
               "grain_policy":"only parsed explicit column lists; group SQL NULL keys together; no inferred non-null requirement",
               "new_model_requests":0,"agent_or_node_sql_executions":0}
    save(ROOT/"records/006_contract_summary.json",summary)
    print(json.dumps({k:v for k,v in summary.items() if k in ('tables','layers','grain_status','summary','missing_tables')},ensure_ascii=False),flush=True)


def main():
    configs = yaml.safe_load(CONFIG.read_text())["examples"]
    originals = {CONFIG}
    inventories = []
    for number in range(1,31):
        location = paths(number,configs)
        originals.update(location[k] for k in ('contract','agent','gold'))
        inventories.append({"task":location['task'],**extract_contract(location['contract'])})
        for side in ('agent','gold'):
            dep = raw_dependency(location[side])
            if dep:originals.add(dep)
    save(ROOT/'records/006_contract_inventory.json',inventories)
    integrity_path = ROOT/'records/006_input_integrity.json'
    print('Hashing original input files',flush=True)
    current = {str(p):fingerprint(p) for p in sorted(originals)}
    if integrity_path.exists():
        before = json.loads(integrity_path.read_text())['before']
        if before!=current:raise RuntimeError('Original inputs differ from the saved checkpoint')
    else:before=current
    save(integrity_path,{'before':before,'after':None,'unchanged':None,'status':'running','files_checked':len(before)})
    def run(number):
        destination = ROOT/f'records/006_contract_impl-{number:03d}.json'
        if destination.exists():
            prior = json.loads(destination.read_text())
            if prior['policy']!=POLICY:raise RuntimeError('Completed task uses a different policy')
            return {'task':f'impl-{number:03d}','reused_completed':True}
        command = [str(PYTHON),str(Path(__file__).resolve()),'--worker',str(number)]
        environment = dict(__import__('os').environ)
        environment.update(PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
        start = time.monotonic()
        with (ROOT/f'records/006_execution_impl-{number:03d}.log').open('w') as log:
            r = subprocess.run(command,env=environment,stdout=log,stderr=subprocess.STDOUT,timeout=7200)
        if r.returncode:raise RuntimeError(f'impl-{number:03d} worker failed; inspect its execution log')
        return {'task':f'impl-{number:03d}','command':command,'returncode':r.returncode,'seconds':round(time.monotonic()-start,3)}
    executions = []
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(run,n) for n in range(1,31)]
            for future in as_completed(futures):
                execution=future.result();executions.append(execution)
                save(ROOT/'records/006_execution.json',executions)
                print('Completed '+execution['task'],flush=True)
        outputs()
    finally:
        after={str(p):fingerprint(p) for p in sorted(originals)}
        save(integrity_path,{'before':before,'after':after,'unchanged':before==after,'status':'finished','files_checked':len(before)})
        if before!=after:raise RuntimeError('An original input file changed')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--worker',type=int);args=parser.parse_args()
    if args.worker:worker(args.worker)
    else:main()
