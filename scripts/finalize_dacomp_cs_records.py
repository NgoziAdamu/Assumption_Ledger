"""Refresh syntax and recognize both constraints/tests in model contract keys."""

from collections import Counter
import csv
import json
from pathlib import Path
import shutil
import tempfile
import duckdb

from compare_dacomp_cs_nodes import WORKSPACE, save
from compare_dacomp_staging import compare_table, fingerprint
from dacomp_sql_extract import key_spec, sql_structure
from dacomp_sql_diff import adaptive_alignment


def atomic_save(path, value):
    temporary = path.with_suffix(".pending")
    save(temporary, value)
    temporary.replace(path)


def main():
    records = WORKSPACE / "records"
    temporary = WORKSPACE / "data/005_final_comparison_tmp"
    temporary.mkdir(exist_ok=True)
    tempfile.tempdir = str(temporary)
    changed, summaries, all_tables, source_commands = [], [], [], []
    checkpoint = WORKSPACE / "data/005_cs_work/input_before.json"
    before = json.loads(checkpoint.read_text())
    for path in sorted(records.glob("005_cs_impl-*.json")):
        detail = json.loads(path.read_text())
        case = Path(detail["private_node_results"]).parent
        log_path = records / f"005_cs_execution_{detail['task']}.log"
        shutil.copyfile(case / "execution.log", log_path)
        source_commands.append({"task": detail["task"], "private_output_directory": str(case),
                                "completed_before_checkpoint": (case / "execution.log").stat().st_mtime_ns < checkpoint.stat().st_mtime_ns,
                                "execution_log": str(log_path.relative_to(WORKSPACE))})
        for table in detail["tables"]:
            table["agent_sql"]["structure"] = sql_structure(table["agent_sql"]["raw_text"])
            spec = key_spec(table["contract"], table["table"])
            has_tests = any(any(t in (c.get("tests") or []) for t in ("not_null", "unique", "primary_key")) for c in spec["columns"])
            comparable = table["current_pred_execution"] and table["gold"]["exists"]
            if has_tests and comparable and table.get("alignment_constraint_format") != "constraints_and_tests_v1":
                previous = table["alignment"]
                with duckdb.connect(detail["private_node_results"], read_only=True) as pred, duckdb.connect(detail["gold_database"], read_only=True) as gold:
                    result = compare_table(pred, gold, table["table"], {"compare_cols": table["official_compare_cols_configured"]}, spec,
                                           table["actual_schema"], table["actual_schema"], alignment_engine=adaptive_alignment)
                table.update(result)
                changed.append({"task": detail["task"], "table": table["table"], "previous_key_columns": previous["columns"],
                                "final_key_columns": table["alignment"]["columns"], "final_reason": table["alignment"].get("reason")})
                print(f"Refreshed {detail['task']} {table['table']}", flush=True)
            table["alignment_constraint_format"] = "constraints_and_tests_v1"
            table["key_contract_interpretation"] = "column constraints and literal tests strings: not_null, unique, primary_key; contract original_text unchanged"
            a = table["alignment"]
            summaries.append({"task": detail["task"], "layer": table["layer"], "table": table["table"],
                              "pred_executed": table["current_pred_execution"], "gold_exists": table["gold"]["exists"],
                              "pred_rows": table["prediction"]["row_count"], "gold_rows": table["gold"]["row_count"],
                              "row_delta": table["row_count_delta_pred_minus_gold"], "key_columns": ";".join(a["columns"]),
                              "key_selection": a.get("reason"), "alignment_status": a["status"],
                              "pred_only_keys": a.get("pred_only_keys"), "gold_only_keys": a.get("gold_only_keys"), "shared_keys": a.get("shared_keys"),
                              "shared_nonunique_groups": a.get("shared_nonunique_key_groups"),
                              "mismatching_official_columns": table["mismatching_official_columns"],
                              "mismatching_all_common_columns": table["mismatching_all_common_columns"],
                              "type_differences": len(table["type_differences"]), "official_current_match": table["official_current_match"],
                              "sql_parse_status": table["agent_sql"]["structure"]["status"], "contract_status": table["contract"]["status"]})
            all_tables.append(table)
        atomic_save(path, detail)
    with (records / "005_cs_summary.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summaries[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(summaries)
    overview_path = records / "005_cs_overview.json"
    overview = json.loads(overview_path.read_text())
    overview.update(alignment_status=dict(Counter(t["alignment"]["status"] for t in all_tables)),
                    key_contract_interpretation="constraints and tests both recognized", sql_parse_status=dict(Counter(t["agent_sql"]["structure"]["status"] for t in all_tables)))
    save(overview_path, overview)
    commands_path = records / "005_cs_execution.json"
    commands = json.loads(commands_path.read_text())
    recorded = {c["task"] for c in commands}
    commands.extend({**c, "reused_completed_result": True, "command": None} for c in source_commands if c["task"] not in recorded)
    save(commands_path, sorted(commands, key=lambda c:c["task"]))
    after = {p: fingerprint(Path(p)) for p in before}
    result = {"tables_recompared": len(changed), "recomparisons": changed,
              "node_sql_reexecutions": 0, "syntax_records_refreshed": len(all_tables),
              "original_inputs_unchanged_since_checkpoint": before == after, "files_checked": len(before),
              "completed_before_checkpoint": [c["task"] for c in source_commands if c["completed_before_checkpoint"]]}
    save(records / "005_cs_finalization.json", result)
    if before != after:
        raise RuntimeError("Original sources changed")
    print(json.dumps({k:v for k,v in result.items() if k!='recomparisons'}), flush=True)


if __name__ == "__main__":
    main()
