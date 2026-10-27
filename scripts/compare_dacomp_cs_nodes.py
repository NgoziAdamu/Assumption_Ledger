"""Rebuild archived CS-failed nodes on isolated gold copies and compare mechanically."""

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys

import duckdb
import yaml

from compare_dacomp_staging import compare_table, fingerprint, quote
from dacomp_sql_extract import contract_blocks, key_spec, sql_structure
from dacomp_sql_diff import adaptive_alignment

WORKSPACE = Path(__file__).resolve().parents[1]
PROJECT = Path("/home/katherine/dac")
SUITE = PROJECT / "benchmarks/DAComp-code/dacomp-de/evaluation_suite"
PYTHON = PROJECT / ".venv-openhands/bin/python"
REVIEW = PROJECT / "runs/20261025_de_batch_review_02"


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def inputs(number, configs):
    short, task = f"impl-{number:03d}", f"dacomp-de-impl-{number:03d}"
    cfg = configs[task]
    score = REVIEW / (f"compatibility/{short}/score.json" if number in (13, 19, 22) else f"scoring/{short}/cs/score.json")
    return {"short": short, "task": task, "cfg": cfg, "score": score,
            "pred_dir": PROJECT / "runs/20261025_de_official_batch_01" / short / "agent" / task,
            "gold_dir": PROJECT / "benchmarks/dacomp-de-gold" / task,
            "contract": PROJECT / "benchmarks/dacomp-de" / task / "docs/data_contract.yaml"}


def targets(info):
    score = json.loads(info["score"].read_text())
    result = []
    for layer in score["partial_evaluation"]["layer_results"]:
        if layer["layer_name"] in ("intermediate", "marts", "mart"):
            for table, match in layer["comparison_results"].items():
                if match is False:
                    result.append({"layer": layer["layer_name"], "table": table,
                                   "archived_pred_execution": layer["pred_execution"].get(table),
                                   "archived_gold_execution": layer["gold_execution"].get(table)})
    return result


class RecordingConnection:
    """Keep official execution/timeout code intact while retaining actual SQL exceptions."""
    def __init__(self, connection):
        self.connection, self.errors = connection, []

    def execute(self, sql, *args, **kwargs):
        try:
            return self.connection.execute(sql, *args, **kwargs)
        except Exception as error:
            self.errors.append({"sql": sql, "exception_type": type(error).__name__, "message": str(error)})
            raise


def worker(number, case):
    sys.path[:0] = [str(SUITE), str(PROJECT / "src")]
    from utils import CSEvaluator, CoreAccuracyEvaluator
    from de_cs_compat import install
    from de_gold_dependencies import install_source_attachment, source_dependency
    configs = yaml.safe_load((SUITE / "evaluation_config_compare.yaml").read_text())["examples"]
    info = inputs(number, configs)
    cfg, gold_path = info["cfg"], info["gold_dir"] / info["cfg"]["database_file"]

    class TaskEvaluator(CSEvaluator):
        pass

    if number in (13, 19, 22):
        install(TaskEvaluator)
    install_source_attachment(TaskEvaluator, gold_path)
    evaluator = TaskEvaluator(info["pred_dir"], info["gold_dir"], cfg, cfg["database_file"])
    hybrid = case / "cs_hybrid.duckdb"
    shutil.copy2(gold_path, hybrid)
    hybrid.chmod(0o600)
    ordered = evaluator._ordered_layers()
    with duckdb.connect(str(gold_path), read_only=True) as gold:
        schemas = {layer: evaluator._resolve_schema_name(gold, layer) for layer in ordered}
        available = {layer: evaluator._list_tables(gold, schemas[layer]) for layer in ordered}
    result = {"task": info["short"], "score_source": str(info["score"]), "compatibility": number in (13, 19, 22),
              "prediction_sql_directory": str(info["pred_dir"]), "gold_database": str(gold_path),
              "source_dependency": str(source_dependency(gold_path)) if source_dependency(gold_path) else None,
              "private_hybrid": str(hybrid), "private_node_results": str(case / "node_results.duckdb"), "tables": []}
    connection = duckdb.connect(str(hybrid))
    alias = evaluator._attach_gold_alias(connection)
    if not alias:
        raise RuntimeError("Read-only gold attachment failed")
    try:
        for target in targets(info):
            layer, table = target["layer"], target["table"]
            schema_name = schemas[layer]
            sql_name = evaluator._sql_name_for_table(layer, table)
            normal = info["pred_dir"] / "sql" / layer / f"{sql_name}.sql"
            candidates = [normal] if normal.is_file() else sorted((info["pred_dir"] / "sql" / layer).rglob(f"{sql_name}.sql"))
            raw = evaluator._read_sql(info["pred_dir"], layer, table)
            used_paths = [str(p) for p in candidates if p.read_text() == raw] if raw else []
            contract = contract_blocks(info["contract"], table)
            recorder = RecordingConnection(connection)
            evaluator._ensure_gold_dependencies(recorder, layer, table, alias, schemas, available, ordered)
            restore_errors = list(recorder.errors)
            recorder.errors.clear()
            ok = evaluator._build_pred_table(recorder, layer, table, schema_name)
            build_errors = list(recorder.errors)
            evaluator._detach_gold_alias(connection, alias)
            connection.close()
            connection = None
            current_match = CoreAccuracyEvaluator(hybrid, gold_path, cfg).compare_table(schema_name, table) if ok else False
            # An unsuccessful CREATE can leave the original gold target in the hybrid.
            # Never report that target as the prediction for a failed execution.
            with duckdb.connect(str(hybrid) if ok else ":memory:", read_only=ok) as pred, duckdb.connect(str(gold_path), read_only=True) as gold:
                table_config = cfg["layers"][layer]["tables"][table]
                table_config = table_config if isinstance(table_config, dict) else {}
                difference = compare_table(pred, gold, table, table_config, key_spec(contract, table), schema_name, schema_name, alignment_engine=adaptive_alignment)
            if ok:
                with duckdb.connect(str(case / "node_results.duckdb")) as snapshot:
                    snapshot.execute("ATTACH '" + str(hybrid).replace("'", "''") + "' AS hybrid (READ_ONLY)")
                    snapshot.execute(f"CREATE SCHEMA IF NOT EXISTS {quote(schema_name)}")
                    snapshot.execute(f"CREATE TABLE {quote(schema_name)}.{quote(table)} AS SELECT * FROM hybrid.{quote(schema_name)}.{quote(table)}")
            difference.update(target)
            difference.update({"actual_schema": schema_name, "current_pred_execution": ok,
                               "official_current_match": current_match, "dependency_restore_errors": restore_errors,
                               "build_errors": build_errors, "prediction_unavailable_reason": None if ok else "missing_sql" if not raw else "official_build_returned_false",
                               "agent_sql": {"used_source_paths": used_paths, "candidate_paths": list(map(str, candidates)),
                                             "raw_text": raw, "official_processed_text": evaluator._process_sql(raw, layer, schema_name),
                                             "structure": sql_structure(raw)},
                               "contract": contract})
            result["tables"].append(difference)
            save(case / "results.json", result)
            print(f"{info['short']} {layer}.{table}: executed={ok}, match={current_match}", flush=True)
            connection = duckdb.connect(str(hybrid))
            alias = evaluator._attach_gold_alias(connection)
            evaluator._copy_table_from_gold(connection, schema_name, table, alias, available[layer])
    finally:
        if connection is not None:
            evaluator._detach_gold_alias(connection, alias)
            connection.close()
    hybrid.unlink()


def impl021():
    contract = PROJECT / "benchmarks/dacomp-de/dacomp-de-impl-021/docs/data_contract.yaml"
    initial_path = PROJECT / "benchmarks/dacomp-de/dacomp-de-impl-021/klaviyo_start.duckdb"
    gold_path = PROJECT / "benchmarks/dacomp-de-gold/dacomp-de-impl-021/klaviyo.duckdb"
    retained_path = PROJECT / "runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/klaviyo.duckdb"
    paths = (initial_path, gold_path, retained_path)
    before = {str(p): fingerprint(p) for p in paths}
    result = {"raw_database": str(gold_path), "gold_database": str(gold_path),
              "initial_repository_raw_database": str(initial_path), "retained_prediction_raw_database": str(retained_path),
              "count_policy": "exact SQL: ID IS NULL; CAST(ID AS VARCHAR) = ''; CAST(ID AS VARCHAR) = 'null'; no trim/lower/coalesce", "tables": []}
    def counts(conn, schema_name, table, column):
        column = quote(column)
        sql = f"SELECT count(*), count(*) FILTER (WHERE {column} IS NULL), count(*) FILTER (WHERE CAST({column} AS VARCHAR)=''), count(*) FILTER (WHERE CAST({column} AS VARCHAR)='null') FROM {quote(schema_name)}.{quote(table)}"
        row = conn.execute(sql).fetchone()
        return {"sql": sql, **dict(zip(["rows", "sql_null", "empty_string", "literal_lowercase_null"], row))}
    with duckdb.connect(str(initial_path), read_only=True) as initial, duckdb.connect(str(gold_path), read_only=True) as gold, duckdb.connect(str(retained_path), read_only=True) as retained:
        for name in ("campaign", "flow", "metric", "person"):
            table, column = f"stg_klaviyo__{name}", f"{name}_id"
            sql_path = gold_path.parent / "sql/staging" / f"{table}.sql"
            result["tables"].append({"table": table, "raw_table": f"raw.{name}", "raw_id_column": "ID", "gold_id_column": column,
                                     "id_mapping_source": str(sql_path), "gold_staging_sql": sql_path.read_text(),
                                     "contract": contract_blocks(contract, table), "raw_counts": counts(gold, "raw", name, "ID"),
                                     "initial_repository_raw_counts": counts(initial, "raw", name, "ID"),
                                     "retained_prediction_raw_counts": counts(retained, "raw", name, "ID"),
                                     "gold_counts": counts(gold, "staging", table, column)})
    after = {str(p): fingerprint(p) for p in paths}
    result["input_integrity"] = {"unchanged": before == after, "before": before, "after": after}
    if before != after:
        raise RuntimeError("impl-021 source database changed")
    return result


def validate_official_flow(number, case):
    """Independent full official CS loop for one plain and one compatibility task."""
    sys.path[:0] = [str(SUITE), str(PROJECT / "src")]
    from utils import CSEvaluator
    from de_cs_compat import install
    from de_gold_dependencies import install_source_attachment, copy_dependencies
    configs = yaml.safe_load((SUITE / "evaluation_config_compare.yaml").read_text())["examples"]
    info = inputs(number, configs)

    class TaskEvaluator(CSEvaluator):
        pass

    if number in (13, 19, 22):
        install(TaskEvaluator)
    private_gold = case / "gold"
    private_gold.mkdir()
    original_gold = info["gold_dir"] / info["cfg"]["database_file"]
    private_database = private_gold / original_gold.name
    shutil.copy2(original_gold, private_database)
    private_database.chmod(0o600)
    copy_dependencies(original_gold, private_database)
    install_source_attachment(TaskEvaluator, private_database)
    pred_dir = case / "prediction"
    shutil.copytree(info["pred_dir"] / "sql", pred_dir / "sql")
    evaluator = TaskEvaluator(pred_dir, private_gold, info["cfg"], info["cfg"]["database_file"])
    score, layers = evaluator.evaluate_all_layers()
    if not layers:
        raise RuntimeError("Official CS returned no evaluated layers")
    save(case / "full_official_cs.json", {"task": info["short"], "score": score, "layers": layers})


def main():
    sys.path[:0] = [str(PROJECT / "src")]
    from safe_env import scrubbed_env
    from de_gold_dependencies import source_dependency
    cfg_path = SUITE / "evaluation_config_compare.yaml"
    configs = yaml.safe_load(cfg_path.read_text())["examples"]
    originals = {cfg_path, SUITE / "utils.py", PROJECT / "src/de_cs_compat.py", PROJECT / "src/de_gold_dependencies.py"}
    infos = [inputs(n, configs) for n in range(1, 31)]
    for info in infos:
        originals.update([info["score"], info["contract"], info["gold_dir"] / info["cfg"]["database_file"]])
        originals.update(info["pred_dir"].glob("sql/**/*.sql"))
        dependency = source_dependency(info["gold_dir"] / info["cfg"]["database_file"])
        if dependency:
            originals.add(dependency)
    originals.add(PROJECT / "benchmarks/dacomp-de/dacomp-de-impl-021/klaviyo_start.duckdb")
    originals.add(PROJECT / "runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/klaviyo.duckdb")
    originals.update((PROJECT / "benchmarks/dacomp-de-gold/dacomp-de-impl-021/sql/staging").glob("*.sql"))
    work = WORKSPACE / "data/005_cs_work"
    work.mkdir(parents=True, exist_ok=True)
    before = {str(p): fingerprint(p) for p in sorted(originals)}
    checkpoint = work / "input_before.json"
    if checkpoint.exists():
        if json.loads(checkpoint.read_text()) != before:
            raise RuntimeError("Inputs changed since the saved checkpoint")
    else:
        save(checkpoint, before)
    all_details, commands = [], []
    reused_tasks = []
    try:
        for number, info in enumerate(infos, 1):
            if not targets(info):
                continue
            destination = WORKSPACE / f"records/005_cs_{info['short']}.json"
            if destination.exists():
                detail = json.loads(destination.read_text())
                if [(t["layer"], t["table"]) for t in detail["tables"]] != [(t["layer"], t["table"]) for t in targets(info)]:
                    raise RuntimeError("Completed output disagrees with final score selection")
                all_details.append(detail)
                reused_tasks.append(info["short"])
                commands.append({"task": info["short"], "reused_completed_record": str(destination),
                                 "completed_before_checkpoint": destination.stat().st_mtime_ns < checkpoint.stat().st_mtime_ns,
                                 "private_output_directory": str(Path(detail["private_node_results"]).parent),
                                 "command": None})
                print(f"Reused completed {info['short']}", flush=True)
                continue
            case = work / info["short"]
            attempt = 1
            while case.exists():
                case = work / f"{info['short']}_retry_{attempt:02d}"
                attempt += 1
            case.mkdir(exist_ok=False)
            (case / ".tmp").mkdir()
            command = [shutil.which("bwrap"), "--ro-bind", "/", "/", "--tmpfs", "/home/katherine",
                       "--ro-bind", str(PROJECT), str(PROJECT), "--ro-bind", str(WORKSPACE), str(WORKSPACE),
                       "--bind", str(case), str(case), "--bind", str(case / ".tmp"), "/tmp",
                       "--unshare-pid", "--proc", "/proc", "--dev", "/dev", "--unshare-net", "--die-with-parent",
                       "--chdir", str(case), "--", str(PYTHON), str(Path(__file__).resolve()), "--worker", str(number), "--case", str(case)]
            environment = scrubbed_env()
            environment.update(PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1",
                               PYTHONPATH=str(WORKSPACE / "data/005_tools"))
            with (case / "execution.log").open("w") as log:
                completed = subprocess.run(command, env=environment, stdout=log, stderr=subprocess.STDOUT, timeout=7200)
            commands.append({"task": info["short"], "command": command, "returncode": completed.returncode})
            if completed.returncode:
                raise RuntimeError(f"{info['short']} failed; see {case / 'execution.log'}")
            detail = json.loads((case / "results.json").read_text())
            all_details.append(detail)
            save(WORKSPACE / f"records/005_cs_{info['short']}.json", detail)
            print(f"Completed {info['short']}: {len(detail['tables'])} nodes", flush=True)
        save(WORKSPACE / "records/005_impl021_id核查.json", impl021())
    finally:
        after = {str(p): fingerprint(p) for p in sorted(originals)}
        save(WORKSPACE / "records/005_cs_input_integrity.json", {"unchanged": before == after, "files_checked": len(before),
             "scope": "checkpointed continuation; earlier completed tasks were executed on read-only mounts before this checkpoint",
             "reused_completed_tasks": reused_tasks, "before": before, "after": after})
        save(WORKSPACE / "records/005_cs_execution.json", commands)
        if before != after:
            raise RuntimeError("Original input files changed")
    summaries = []
    for detail in all_details:
        for t in detail["tables"]:
            a = t["alignment"]
            summaries.append({"task": detail["task"], "layer": t["layer"], "table": t["table"],
                              "pred_executed": t["current_pred_execution"], "gold_exists": t["gold"]["exists"],
                              "pred_rows": t["prediction"]["row_count"], "gold_rows": t["gold"]["row_count"],
                              "row_delta": t["row_count_delta_pred_minus_gold"], "key_columns": ";".join(a["columns"]),
                              "key_selection": a.get("reason"), "alignment_status": a["status"],
                              "pred_only_keys": a.get("pred_only_keys"), "gold_only_keys": a.get("gold_only_keys"), "shared_keys": a.get("shared_keys"),
                              "shared_nonunique_groups": a.get("shared_nonunique_key_groups"),
                              "mismatching_official_columns": t["mismatching_official_columns"],
                              "mismatching_all_common_columns": t["mismatching_all_common_columns"],
                              "type_differences": len(t["type_differences"]), "official_current_match": t["official_current_match"],
                              "sql_parse_status": t["agent_sql"]["structure"]["status"], "contract_status": t["contract"]["status"]})
    with (WORKSPACE / "records/005_cs_summary.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summaries[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(summaries)
    overview = {"created_at_utc": datetime.now(timezone.utc).isoformat(), "python": sys.version.split()[0], "duckdb": duckdb.__version__,
                "failed_nodes": len(summaries), "tasks_with_failed_nodes": len(all_details), "layers": dict(Counter(t["layer"] for t in summaries)),
                "executed": sum(t["pred_executed"] for t in summaries), "gold_missing": sum(not t["gold_exists"] for t in summaries),
                "reproduced_matches": sum(t["official_current_match"] for t in summaries),
                "prediction_execution_disagreements": [{"task": d["task"], "table": t["table"]} for d in all_details for t in d["tables"] if t["archived_pred_execution"] != t["current_pred_execution"]],
                "dependency_restore_error_nodes": sum(bool(t["dependency_restore_errors"]) for d in all_details for t in d["tables"]),
                "sql_parse_status": dict(Counter(t["sql_parse_status"] for t in summaries)), "contract_status": dict(Counter(t["contract_status"] for t in summaries)),
                "alignment_status": dict(Counter(t["alignment_status"] for t in summaries)),
                "normalization": "COALESCE(LOWER(TRIM(CAST(column AS VARCHAR))), 'null')", "round_numeric_values": False,
                "globally_ignore_time_columns": False, "model_requests": 0, "agent_reruns": 0, "input_files_unchanged": True,
                "not_included_other_layers": [{"task": i["short"], "layer": l["layer_name"], "failed_tables": [t for t,v in l["comparison_results"].items() if v is False]} for i in infos for l in json.loads(i["score"].read_text())["partial_evaluation"]["layer_results"] if l["layer_name"] not in ("staging", "intermediate", "marts", "mart")]}
    save(WORKSPACE / "records/005_cs_overview.json", overview)
    print(json.dumps(overview, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", type=int)
    parser.add_argument("--case", type=Path)
    parser.add_argument("--validate-official", type=int)
    args = parser.parse_args()
    if args.validate_official:
        validate_official_flow(args.validate_official, args.case)
    elif args.worker:
        worker(args.worker, args.case)
    else:
        main()
