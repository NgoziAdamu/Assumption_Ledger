"""Verify an exported DAComp handover without executing its recorded commands."""

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import re


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def audit(source, records):
    records.mkdir(exist_ok=True)
    handover = (source / "HANDOVER.md").read_text()
    listing = handover.split("path\tbytes\tsha256\n", 1)[1].split("```", 1)[0]
    expected = list(csv.DictReader(io.StringIO("path\tbytes\tsha256\n" + listing), delimiter="\t"))
    files = sorted(p for p in source.rglob("*") if p.is_file())
    actual = {p.relative_to(source).as_posix(): p for p in files}
    missing, mismatches, inventory = [], [], []
    for row in expected:
        path = actual.get(row["path"])
        if path is None:
            missing.append(row["path"])
        elif path.stat().st_size != int(row["bytes"]) or sha256(path) != row["sha256"]:
            mismatches.append(row["path"])
    extras = sorted(set(actual) - {r["path"] for r in expected} - {"HANDOVER.md"})
    canonical_logs = {}
    for name, path in actual.items():
        content = path.read_bytes()
        entry = {"path": name, "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}
        parts = path.relative_to(source).parts
        reason = None
        if parts[0] == "analysis":
            reason = "prior_project_analysis"
        elif name == "HANDOVER.md":
            reason = "kept_uncompressed"
        elif path.suffix.lower() in {".duckdb", ".db", ".parquet", ".pkl", ".pyc", ".so"}:
            reason = "binary_or_database"
        elif any(x in parts for x in ("event_cache", "__pycache__", ".venv", "venv", ".agent-python")):
            reason = "cache_or_environment"
        elif path.name == "convo_stats.json":
            # These files contain Base64-encoded pickle statistics, not JSON.
            reason = "serialized_session_cache"
        elif ".tmp" in parts or path.suffix == ".tmp":
            reason = "temporary_workspace"
        else:
            try:
                content.decode("utf-8")
            except UnicodeDecodeError:
                reason = "binary_content"
        if reason is None and path.suffix == ".log":
            if entry["sha256"] in canonical_logs:
                reason = "identical_log_copy"
                entry["duplicate_of"] = canonical_logs[entry["sha256"]]
            else:
                canonical_logs[entry["sha256"]] = name
        entry["disposition"] = reason or "archive"
        inventory.append(entry)
    save(records / "003_dacomp_inventory.json", inventory)

    batch = source / "runs/20261025_de_official_batch_01"
    review = source / "runs/20261025_de_batch_review_02"
    score_rows, score_checks, event_checks = [], [], []
    old_summary = {r["task"]: r for r in csv.DictReader((source / "analysis/20261025_de_batch_review_01/reviewed_task_summary.csv").open())}
    table_rows = {}
    for line in handover.splitlines():
        if re.match(r"\| impl-\d{3} \|", line):
            columns = [x.strip() for x in line.strip("|").split("|")]
            if len(columns) == 9:
                table_rows[columns[0]] = columns
    sample = None
    for number in range(1, 31):
        task = f"impl-{number:03}"
        full_task = f"dacomp-de-{task}"
        agent = batch / task / "agent"
        cfs_path = review / "scoring" / task / "cfs/score.json"
        cs_path = (review / "compatibility" / task / "score.json" if number in {13, 19, 22}
                   else review / "scoring" / task / "cs/score.json")
        cfs, cs = load(cfs_path)["final_score"], load(cs_path)["final_score"]
        summary = load(batch / task / "run_summary.json")
        result = load(agent / full_task / "result.json")
        columns = table_rows[task]
        previous = old_summary[full_task]
        score_checks.append({
            "task": task, "cfs": cfs, "cs": cs,
            "handover_cfs": columns[3], "handover_cs": columns[4],
            "handover_matches": f"{cfs:.6f}" == columns[3] and f"{cs:.6f}" == columns[4].replace(" *", ""),
            "previous_csv_matches": cfs == float(previous["cfs"]) and cs == float(previous["cs"]),
            "cfs_source": str(cfs_path.relative_to(source)), "cs_source": str(cs_path.relative_to(source)),
        })
        score_rows.append({"task": task, "batch_status": summary.get("status"),
                           "result_status": result.get("status"), "run_py_success": result.get("run_py_success"),
                           "cfs": cfs, "cs": cs,
                           "cfs_source": str(cfs_path.relative_to(source)), "cs_source": str(cs_path.relative_to(source))})
        event_files = sorted(agent.glob(".events/sessions/*/events/*.json"))
        events = [load(p) for p in event_files]
        runs = [e for e in events if e.get("source") == "agent" and e.get("action") == "run"]
        finishes = [e for e in events if e.get("action") == "finish"]
        counts = Counter()
        problems = []
        recorded_errors = []
        executed_ids = []
        for event in runs:
            response = (event.get("tool_call_metadata") or {}).get("model_response") or {}
            messages = [c.get("message", {}) for c in response.get("choices", [])]
            command = event.get("args", {}).get("command")
            tool_id = (event.get("tool_call_metadata") or {}).get("tool_call_id")
            matched = False
            for message in messages:
                for call in message.get("tool_calls") or []:
                    if call.get("id") == tool_id:
                        arguments = json.loads(call["function"]["arguments"])
                        matched = arguments.get("command") == command
            observations = [e for e in events if e.get("observation") in {"run", "error"} and e.get("cause") == event["id"]]
            normal = [e for e in observations if e.get("observation") == "run"]
            errors = [e for e in observations if e.get("observation") == "error"]
            if normal:
                executed_ids.append(event["id"])
            for error in errors:
                recorded_errors.append({"action_id": event["id"], "observation_id": error["id"],
                                        "observation_type": "error", "exit_code_present": False,
                                        "message_tail": error.get("content", "")[-24:]})
            has_exit = any("exit_code" in e.get("extras", {}).get("metadata", {}) for e in observations)
            has_output = any(isinstance(e.get("content"), str) for e in observations)
            counts.update({"model_output_present": bool(messages), "tool_command_matches": matched,
                           "observation_linked": bool(observations), "exit_code_present": has_exit,
                           "output_field_present": has_output, "run_observations": bool(normal),
                           "error_observations": bool(errors)})
            if not all([messages, matched, observations, has_output]) or (normal and not has_exit):
                problems.append({"event_id": event["id"], "model_response": bool(messages),
                                 "command_matches": matched, "observations": len(observations),
                                 "exit_code": has_exit, "output": has_output})
        commands = [json.loads(line) for line in (agent / "sidecar" / full_task / "commands.jsonl").read_text().splitlines()]
        command_ids = [x["event_id"] for x in commands if x.get("agent_command_sequence") is not None]
        sql_files = list((agent / full_task / "sql").rglob("*.sql"))
        output = load(agent / "output.jsonl")
        event_checks.append({"task": task, "native_events": len(events), "bash_actions": len(runs),
                             "finish_actions": len(finishes), **dict(counts), "problems": problems,
                             "recorded_tool_errors": recorded_errors,
                             "command_index_matches": sorted(command_ids) == sorted(e["id"] for e in runs),
                             "command_index_matches_run_observations": sorted(command_ids) == sorted(executed_ids),
                             "action_ids_not_in_command_index": sorted({e["id"] for e in runs} - set(command_ids)),
                             "handover_command_count_matches": len(runs) == int(columns[7]),
                             "final_sql_files": len(sql_files), "handover_sql_count_matches": len(sql_files) == int(columns[8]),
                             "output_top_level_fields": sorted(output), "history_pairs": len(output["history"])})
        if number == 23:
            action = next(e for e in events if e.get("id") == 49)
            observation = next(e for e in events if e.get("cause") == 49 and e.get("observation") == "run")
            sample = {"task": task, "selection_basis": "archived CFS final_score = 0; no error interpretation",
                      "action": action, "observation": observation,
                      "action_path": str(next(p for p in event_files if p.stem == "49").relative_to(source)),
                      "observation_path": str(next(p for p in event_files if p.stem == str(observation["id"])).relative_to(source))}
    with (records / "003_dacomp_task_scores.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(score_rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(score_rows)
    save(records / "003_dacomp_score_checks.json", score_checks)
    save(records / "003_dacomp_event_checks.json", event_checks)
    save(records / "003_dacomp_impl023_sample.json", sample)
    version_count, deletion_count, version_errors = 0, 0, []
    for index in batch.glob("impl-*/agent/sidecar/*/sql_changes.jsonl"):
        for line in index.read_text().splitlines():
            change = json.loads(line)
            if change.get("deleted"):
                deletion_count += 1
                continue
            version_count += 1
            content = index.parent / change["content_file"]
            if (not content.is_file() or content.stat().st_size != change["bytes"]
                    or sha256(content) != change["sha256"]):
                version_errors.append({"index": str(index), "content_file": change["content_file"]})
    save(records / "003_dacomp_sql_version_checks.json", {
        "indexed_content_versions": version_count, "deletion_markers": deletion_count,
        "size_or_hash_mismatches": version_errors,
    })
    groups = defaultdict(lambda: {"files": 0, "bytes": 0})
    for row in inventory:
        group = groups[row["disposition"]]; group["files"] += 1; group["bytes"] += row["bytes"]
    summary = {"source": str(source), "handover_listed_files": len(expected),
               "handover_listed_bytes": sum(int(x["bytes"]) for x in expected),
               "actual_files": len(files), "actual_bytes": sum(p.stat().st_size for p in files),
               "missing": missing, "unexpected": extras, "size_or_hash_mismatch": mismatches,
               "score_tasks": len(score_checks), "handover_score_matches": sum(x["handover_matches"] for x in score_checks),
               "previous_csv_score_matches": sum(x["previous_csv_matches"] for x in score_checks),
               "event_tasks": len(event_checks), "bash_actions": sum(x["bash_actions"] for x in event_checks),
               "event_problems": sum(len(x["problems"]) for x in event_checks),
               "command_indices_match_all_actions": all(x["command_index_matches"] for x in event_checks),
               "command_indices_match_run_observations": all(x["command_index_matches_run_observations"] for x in event_checks),
               "run_observations": sum(x["run_observations"] for x in event_checks),
               "error_observations": sum(x["error_observations"] for x in event_checks),
               "handover_counts_match": all(x["handover_command_count_matches"] and x["handover_sql_count_matches"] for x in event_checks),
               "disposition": dict(groups)}
    save(records / "003_dacomp_audit_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("data/dacomp_deimpl_prev"))
    parser.add_argument("--records", type=Path, default=Path("records"))
    args = parser.parse_args()
    audit(args.source, args.records)
