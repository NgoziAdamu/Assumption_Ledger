"""Mechanically compare retained, CFS-mismatched staging tables; never run pipelines."""

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

import duckdb
import yaml
from yaml.nodes import MappingNode, ScalarNode, SequenceNode


def quote(name):
    return '"' + name.replace('"', '""') + '"'


def fingerprint(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(4 * 1024 * 1024):
            digest.update(block)
    stat = path.stat()
    return {"bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns, "sha256": digest.hexdigest()}


def plain(node):
    if isinstance(node, MappingNode):
        return {key.value: plain(value) for key, value in node.value}
    if isinstance(node, SequenceNode):
        return [plain(value) for value in node.value]
    return node.value if isinstance(node, ScalarNode) else None


def contracts(path):
    text = path.read_text()
    try:
        node = yaml.compose(text)
        mode = "strict"
    except yaml.YAMLError:
        node = yaml.compose(text.replace("\\", "\\\\"))
        mode = "escape_backslashes_in_memory_for_names_and_constraints_only"
    value = plain(node)
    tables = value["staging_contract"]["tables"]
    tables = {x["name"]: x for x in tables} if isinstance(tables, list) else tables
    return tables, mode


def schema(connection, table):
    rows = connection.execute("SELECT column_name, data_type FROM information_schema.columns "
                              "WHERE table_schema='staging' AND table_name=? ORDER BY ordinal_position", [table]).fetchall()
    if not rows:
        return {"exists": False, "row_count": None, "columns": []}
    count = connection.execute("SELECT count(*) FROM staging." + quote(table)).fetchone()[0]
    return {"exists": True, "row_count": count,
            "columns": [{"name": name, "type": kind} for name, kind in rows]}


def constraints(column):
    values = column.get("constraints") or []
    return [str(x).lower().replace(" ", "_") for x in ([values] if isinstance(values, str) else values)]


def read_rows(connection, table, columns):
    expressions = []
    for column in columns:
        raw = "CAST(" + quote(column) + " AS VARCHAR)"
        expressions.extend(["COALESCE(LOWER(TRIM(" + raw + ")), 'null')", raw])
    return connection.execute("SELECT " + ",".join(expressions) + " FROM staging." + quote(table)).fetchall()


def key_candidates(spec, columns):
    result = []
    def add(names, reason):
        if isinstance(names, str):
            names = [names]
        if names and all(x in columns for x in names) and names not in [r["columns"] for r in result]:
            result.append({"columns": list(names), "reason": reason})
    declared = spec.get("primary_key") or spec.get("primary_keys")
    add(declared, "contract_declared_primary_key")
    items = spec.get("columns", [])
    items = list(items.values()) if isinstance(items, dict) else items
    definitions = {c["name"]: c for c in items}
    required_ids = [c for c in columns if (c == "id" or c.endswith("_id"))
                    and "not_null" in constraints(definitions.get(c, {}))]
    for name in required_ids:
        if "unique" in constraints(definitions[name]) or "primary_key" in constraints(definitions[name]):
            add([name], "contract_not_null_unique_id")
    for name, item in definitions.items():
        if "primary_key" in constraints(item):
            add([name], "contract_column_primary_key")
    # Keep explicit contract keys even when the data does not make them unique.
    if result:
        return result[:1], required_ids
    entity = spec.get("name", "").split("__")[-1]
    for suffix in ("_history", "_stats", "_report"):
        entity = entity.removesuffix(suffix)
    entity_id = entity + "_id"
    if entity_id in required_ids:
        add([entity_id], "contract_not_null_entity_id")
    add(required_ids, "contract_not_null_id_columns")
    for name, item in definitions.items():
        if "unique" in constraints(item):
            add([name], "contract_unique_non_id_or_unspecified_nullability")
    for name in columns:
        if name.endswith("_key"):
            add([name], "inferred_named_key")
    for name in (entity_id, "id"):
        add([name], "inferred_entity_id_not_declared_not_null")
    # These are explicitly recorded fallback partitions, not asserted primary keys.
    dimensions = [c for c in columns if (c.endswith(("_id", "_key", "_code", "_index")) or c in {
        "date_day", "date", "report_date", "package_name", "app_version", "device", "country",
        "os_version", "traffic_source", "region", "state", "ad_network_type", "placement"})
        and not c.startswith(("_dbt", "_fivetran"))]
    add(list(dict.fromkeys(required_ids + dimensions)), "inferred_id_date_dimension_composite")
    for name in columns:
        if name.endswith("_id"):
            add([name], "inferred_available_id")
    if not result and columns:
        required = [c for c in columns if "not_null" in constraints(definitions.get(c, {}))]
        add(required or columns[:1], "fallback_required_columns_or_first_common_column")
    return result, required_ids


def group_rows(rows, indices):
    grouped = defaultdict(list)
    for row in rows:
        grouped[tuple(row[2 * i] for i in indices)].append(row)
    return grouped


def align_and_compare(pred_rows, gold_rows, columns, spec, official_columns):
    candidates, required_ids = key_candidates(spec, columns)
    profiles = []
    selected = None
    for candidate in candidates:
        indices = [columns.index(c) for c in candidate["columns"]]
        p = group_rows(pred_rows, indices)
        g = group_rows(gold_rows, indices)
        profile = {**candidate, "pred_distinct_keys": len(p), "gold_distinct_keys": len(g),
                   "pred_duplicate_key_groups": sum(len(v) > 1 for v in p.values()),
                   "gold_duplicate_key_groups": sum(len(v) > 1 for v in g.values())}
        profiles.append(profile)
        if selected is None:
            selected = (profile, indices)
        if candidate["reason"].startswith("contract_declared") or "unique" in candidate["reason"] or "primary_key" in candidate["reason"]:
            selected = (profile, indices)
            break
        if not profile["pred_duplicate_key_groups"] and not profile["gold_duplicate_key_groups"]:
            selected = (profile, indices)
            break
    if selected is None:
        return {"status": "no_common_key_columns", "columns": []}, []
    # If no candidate is unique, prefer the recorded dimension composite over a bare foreign ID.
    if all(x["pred_duplicate_key_groups"] or x["gold_duplicate_key_groups"] for x in profiles):
        composite = next((x for x in profiles if x["reason"] == "inferred_id_date_dimension_composite"), None)
        if composite and not selected[0]["reason"].startswith(("contract_declared", "contract_not_null_unique", "contract_unique", "contract_column_primary")):
            selected = (composite, [columns.index(c) for c in composite["columns"]])
    selection, indices = selected
    p, g = group_rows(pred_rows, indices), group_rows(gold_rows, indices)
    shared = sorted(set(p) & set(g))
    ambiguous = [k for k in shared if len(p[k]) != 1 or len(g[k]) != 1]
    alignment = {**selection, "status": "grouped_nonunique_keys" if ambiguous else "unique_shared_keys",
                 "contract_not_null_id_candidates": required_ids, "candidate_profiles": profiles,
                 "pred_only_keys": len(set(p) - set(g)), "gold_only_keys": len(set(g) - set(p)),
                 "shared_keys": len(shared), "shared_one_to_one_keys": len(shared) - len(ambiguous),
                 "shared_nonunique_key_groups": len(ambiguous),
                 "pred_rows_in_shared_nonunique_groups": sum(len(p[k]) for k in ambiguous),
                 "gold_rows_in_shared_nonunique_groups": sum(len(g[k]) for k in ambiguous),
                 "pred_null_key_rows": sum(any(row[2 * i + 1] is None for i in indices) for row in pred_rows),
                 "gold_null_key_rows": sum(any(row[2 * i + 1] is None for i in indices) for row in gold_rows),
                 "pred_empty_key_rows": sum(any(row[2 * i] == "" for i in indices) for row in pred_rows),
                 "gold_empty_key_rows": sum(any(row[2 * i] == "" for i in indices) for row in gold_rows)}
    differences = []
    for i, column in enumerate(columns):
        exact, minimum, pred_unpaired, gold_unpaired = 0, 0, 0, 0
        samples = []
        for key in shared:
            pr, gr = p[key], g[key]
            if len(pr) == len(gr) == 1:
                if pr[0][2 * i] != gr[0][2 * i]:
                    exact += 1
                    pred_unpaired += 1
                    gold_unpaired += 1
                    if len(samples) < 3:
                        samples.append({"kind": "one_to_one", "key": dict(zip(selection["columns"], key)),
                                        "prediction_value": pr[0][2 * i + 1], "gold_value": gr[0][2 * i + 1],
                                        "prediction_normalized": pr[0][2 * i], "gold_normalized": gr[0][2 * i]})
                continue
            pc, gc = Counter(r[2 * i] for r in pr), Counter(r[2 * i] for r in gr)
            pu, gu = pc - gc, gc - pc
            pn, gn = sum(pu.values()), sum(gu.values())
            pred_unpaired += pn
            gold_unpaired += gn
            minimum += min(pn, gn)
            if pn and gn and len(samples) < 3:
                def residual_values(rows, counts):
                    values = {}
                    for row in rows:
                        if row[2 * i] in counts:
                            values.setdefault(row[2 * i], row[2 * i + 1])
                    return [{"value": values[v], "normalized": v, "rows": counts[v]} for v in sorted(counts)[:3]]
                samples.append({"kind": "nonunique_key_multisets_not_a_row_pair",
                                "key": dict(zip(selection["columns"], key)),
                                "prediction_unmatched_values": residual_values(pr, pu),
                                "gold_unmatched_values": residual_values(gr, gu),
                                "minimum_different_value_pairs": min(pn, gn)})
        differences.append({"column": column, "included_in_official_comparison": column in official_columns,
                            "one_to_one_mismatch_rows": exact,
                            "nonunique_key_minimum_value_mismatch_pairs": minimum,
                            "mismatch_rows_or_minimum_pairs": exact + minimum,
                            "pred_unmatched_value_occurrences": pred_unpaired,
                            "gold_unmatched_value_occurrences": gold_unpaired,
                            "count_semantics": "minimum_value_mismatch_pairs" if ambiguous else "exact_one_to_one_rows",
                            "examples": samples})
    return alignment, differences


def compare_table(pred, gold, table, table_config, spec):
    pm, gm = schema(pred, table), schema(gold, table)
    ptypes = {x["name"]: x["type"] for x in pm["columns"]}
    gtypes = {x["name"]: x["type"] for x in gm["columns"]}
    gmapping, pmapping = {c.lower(): c for c in gtypes}, {c.lower(): c for c in ptypes}
    common = [c for c in gtypes if c.lower() in pmapping]
    allowed = table_config.get("compare_cols") or []
    official = [gmapping[c.lower()] for c in allowed if c.lower() in gmapping and c.lower() in pmapping] if allowed else common
    result = {"table": table, "prediction": pm, "gold": gm,
              "row_count_delta_pred_minus_gold": pm["row_count"] - gm["row_count"] if pm["exists"] and gm["exists"] else None,
              "pred_only_columns": [c for c in ptypes if c not in gtypes],
              "gold_only_columns": [c for c in gtypes if c not in ptypes],
              "type_differences": [{"column": c, "prediction_type": ptypes[pmapping[c.lower()]], "gold_type": gtypes[c]} for c in common if ptypes[pmapping[c.lower()]] != gtypes[c]],
              "official_compare_cols_configured": allowed, "official_compare_cols_available": official,
              "columns_outside_official_comparison": [c for c in common if c not in official],
              "case_only_column_name_differences": [{"prediction_name": pmapping[k], "gold_name": gmapping[k]} for k in gmapping.keys() & pmapping.keys() if gmapping[k] != pmapping[k]]}
    if not pm["exists"] or not gm["exists"] or not common:
        result.update(alignment={"status": "missing_table_or_no_common_columns", "columns": []}, column_differences=[])
    else:
        pr, gr = read_rows(pred, table, common), read_rows(gold, table, common)
        result["alignment"], result["column_differences"] = align_and_compare(pr, gr, common, spec, official)
    result["mismatching_official_columns"] = sum(c["included_in_official_comparison"] and c["mismatch_rows_or_minimum_pairs"] > 0 for c in result["column_differences"])
    result["mismatching_all_common_columns"] = sum(c["mismatch_rows_or_minimum_pairs"] > 0 for c in result["column_differences"])
    if result["alignment"]["status"] in {"missing_table_or_no_common_columns", "no_common_key_columns"}:
        result["mismatching_official_columns"] = result["mismatching_all_common_columns"] = None
    return result


def main(project, output, export):
    suite = project / "benchmarks/DAComp-code/dacomp-de/evaluation_suite"
    sys.path.insert(0, str(suite))
    from utils import CoreAccuracyEvaluator
    config_path = suite / "evaluation_config_compare.yaml"
    config = yaml.safe_load(config_path.read_text())["examples"]
    output.mkdir(exist_ok=True)
    originals = {str(config_path), str(suite / "utils.py")}
    for number in range(1, 31):
        task, short = f"dacomp-de-impl-{number:03}", f"impl-{number:03}"
        originals.update(map(str, [project / "benchmarks/dacomp-de" / task / "docs/data_contract.yaml",
                                  project / "benchmarks/dacomp-de-gold" / task / config[task]["database_file"],
                                  project / "runs/20261025_de_official_batch_01" / short / "agent" / task / config[task]["database_file"],
                                  export / "runs/20261025_de_batch_review_02/scoring" / short / "cfs/score.json"]))
    print("Hashing read-only input files before comparison", flush=True)
    before = {p: fingerprint(Path(p)) for p in sorted(originals)}
    summaries, task_summaries = [], []
    try:
        for number in range(1, 31):
            task, short = f"dacomp-de-impl-{number:03}", f"impl-{number:03}"
            cfg = config[task]
            pred_path = project / "runs/20261025_de_official_batch_01" / short / "agent" / task / cfg["database_file"]
            gold_path = project / "benchmarks/dacomp-de-gold" / task / cfg["database_file"]
            contract_path = project / "benchmarks/dacomp-de" / task / "docs/data_contract.yaml"
            specs, parse_mode = contracts(contract_path)
            score_path = export / "runs/20261025_de_batch_review_02/scoring" / short / "cfs/score.json"
            score = json.loads(score_path.read_text())
            matches = next(x for x in score["partial_evaluation"]["layer_results"] if x["layer_name"] == "staging")["comparison_results"]
            failed = [t for t in cfg["layers"]["staging"]["tables"] if matches[t] is False]
            details = {"task": short, "prediction_database": str(pred_path), "gold_database": str(gold_path),
                       "contract": str(contract_path), "contract_parse_mode": parse_mode,
                       "cfs_score_source": str(score_path), "configured_staging_tables": len(matches), "tables": []}
            evaluator = CoreAccuracyEvaluator(pred_path, gold_path, cfg)
            with duckdb.connect(str(pred_path), read_only=True) as pred, duckdb.connect(str(gold_path), read_only=True) as gold:
                details["duckdb_timezone"] = {"prediction": pred.execute("SELECT current_setting('TimeZone')").fetchone()[0],
                                              "gold": gold.execute("SELECT current_setting('TimeZone')").fetchone()[0]}
                for table in failed:
                    result = compare_table(pred, gold, table, cfg["layers"]["staging"]["tables"][table], specs.get(table, {}))
                    result["archived_cfs_match"] = False
                    result["official_current_match"] = evaluator.compare_table("staging", table)
                    details["tables"].append(result)
                    a = result["alignment"]
                    summaries.append({"task": short, "table": table,
                                      "pred_rows": result["prediction"]["row_count"], "gold_rows": result["gold"]["row_count"],
                                      "row_delta": result["row_count_delta_pred_minus_gold"], "key_columns": ";".join(a["columns"]),
                                      "key_selection": a.get("reason"), "alignment_status": a["status"],
                                      "pred_only_keys": a.get("pred_only_keys"), "gold_only_keys": a.get("gold_only_keys"),
                                      "shared_keys": a.get("shared_keys"), "shared_nonunique_groups": a.get("shared_nonunique_key_groups"),
                                      "mismatching_official_columns": result["mismatching_official_columns"],
                                      "mismatching_all_common_columns": result["mismatching_all_common_columns"],
                                      "type_differences": len(result["type_differences"]),
                                      "official_current_match": result["official_current_match"]})
            (output / f"004_staging_{short}.json").write_text(json.dumps(details, ensure_ascii=False, indent=2) + "\n")
            task_summaries.append({"task": short, "configured_staging_tables": len(matches), "archived_cfs_failed_tables": len(failed),
                                   "missing_tables_or_columns": sum(t["alignment"]["status"] == "missing_table_or_no_common_columns" for t in details["tables"]),
                                   "shared_nonunique_key_tables": sum(t["alignment"]["status"] == "grouped_nonunique_keys" for t in details["tables"])})
            print(f"Completed {short}: {len(failed)} staging tables", flush=True)
    finally:
        after = {p: fingerprint(Path(p)) for p in sorted(originals)}
        integrity = {"unchanged": before == after, "files_checked": len(before), "before": before, "after": after}
        (output / "004_staging_input_integrity.json").write_text(json.dumps(integrity, indent=2) + "\n")
        if before != after:
            raise RuntimeError("A source file changed during read-only comparison.")
    with (output / "004_staging_summary.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summaries[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(summaries)
    overview = {"created_at_utc": datetime.now(timezone.utc).isoformat(), "python": sys.version.split()[0], "duckdb": duckdb.__version__,
                "official_utils_sha256": before[str(suite / "utils.py")]["sha256"],
                "tasks": task_summaries, "total_configured_staging_tables": sum(x["configured_staging_tables"] for x in task_summaries),
                "total_compared_tables": len(summaries), "official_current_matches_in_archived_failure_set": sum(x["official_current_match"] for x in summaries),
                "shared_nonunique_key_tables": sum(x["alignment_status"] == "grouped_nonunique_keys" for x in summaries),
                "missing_tables_or_columns": sum(x["alignment_status"] == "missing_table_or_no_common_columns" for x in summaries),
                "normalization": "COALESCE(LOWER(TRIM(CAST(column AS VARCHAR))), 'null')",
                "round_numeric_values": False, "globally_ignore_time_columns": False,
                "column_selection": "official compare_cols intersection; all common columns additionally reported",
                "null_and_empty_key_policy": "retain normalized 'null' and empty-string key groups; report their row counts",
                "duplicate_key_policy": "one-to-one keys: exact row differences; nonunique shared keys: per-column multiset cancellation and minimum unequal-value pairs, never a Cartesian join",
                "examples": "up to three differing keys per column; fewer when fewer exist; nonunique-key examples are residual value multisets, not asserted row pairs",
                "new_model_requests": 0, "agent_or_pipeline_reruns": 0, "input_files_unchanged": True}
    (output / "004_staging_overview.json").write_text(json.dumps(overview, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: overview[k] for k in ("total_compared_tables", "shared_nonunique_key_tables", "missing_tables_or_columns", "official_current_matches_in_archived_failure_set")}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path("/home/katherine/dac"))
    parser.add_argument("--output", type=Path, default=Path("records"))
    parser.add_argument("--export", type=Path, default=Path("data/dacomp_deimpl_prev"))
    args = parser.parse_args()
    main(args.project, args.output, args.export)
