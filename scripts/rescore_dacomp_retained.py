"""Recheck one retained task using existing official comparison code on private copies."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(project, output, records):
    sys.path.insert(0, str(project / "src"))
    from de_batch_review import score_job
    import duckdb
    import yaml

    suite = project / "benchmarks/DAComp-code/dacomp-de/evaluation_suite"
    task = "dacomp-de-impl-023"
    config = yaml.safe_load((suite / "evaluation_config_compare.yaml").read_text())["examples"][task]
    source = project / "runs/20261025_de_official_batch_01/impl-023/agent" / task
    initial = project / "benchmarks/dacomp-de" / task
    gold = project / "benchmarks/dacomp-de-gold" / task
    protected = [source / config["database_file"], gold / config["database_file"],
                 initial / "social_media_reporting_start.duckdb", initial / "run.py",
                 suite / "utils.py", suite / "evaluation_config_compare.yaml"]
    protected += sorted((source / "sql").rglob("*.sql"))
    protected += sorted((gold / "sql").rglob("*.sql"))
    before = {str(p): {"sha256": digest(p), "bytes": p.stat().st_size,
                       "mtime_ns": p.stat().st_mtime_ns} for p in protected}
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    completed = []
    try:
        for mode in ("cfs", "cs"):
            result = score_job((task, mode, output, config, False))
            completed.append(result)
            case = output / "scoring/impl-023" / mode
            for name in ("score.json", "score.log", "execution.json"):
                if (case / name).exists():
                    shutil.copyfile(case / name, records / f"003_dacomp_impl023_{mode}_{name}")
            print(json.dumps({k: result.get(k) for k in ("task", "mode", "returncode", "score", "evaluation_complete", "elapsed_seconds")}), flush=True)
            if result["returncode"] != 0 or not result["evaluation_complete"]:
                raise RuntimeError("The evaluator did not complete; preserve the new files for review.")
    finally:
        after = {str(p): {"sha256": digest(p), "bytes": p.stat().st_size,
                          "mtime_ns": p.stat().st_mtime_ns} for p in protected}
        integrity = {"unchanged": before == after, "files_checked": len(before),
                     "before": before, "after": after}
        (records / "003_dacomp_rescore_integrity.json").write_text(json.dumps(integrity, indent=2) + "\n")
        if before != after:
            raise RuntimeError("A protected source file changed.")
    original = project / "runs/20261025_de_batch_review_02/scoring/impl-023"
    summary = {"task": task, "python": sys.version.split()[0], "duckdb": duckdb.__version__,
               "official_comparison_source": str(suite / "utils.py"),
               "official_comparison_sha256": digest(suite / "utils.py"),
               "execution_wrapper": str(project / "src/de_retained_score.py"),
               "execution_wrapper_sha256": digest(project / "src/de_retained_score.py"),
               "reconstruction_gate": "readonly database existence check; run.py is not executed",
               "cs_compatibility_fixes": False, "network_enabled": False,
               "new_model_requests": 0, "source_unchanged": True, "results": []}
    for row in completed:
        old = json.loads((original / row["mode"] / "score.json").read_text())
        new = json.loads((output / "scoring/impl-023" / row["mode"] / "score.json").read_text())
        def comparison_only(value):
            return {k: v for k, v in value.items() if k != "timestamp"}
        summary["results"].append({"mode": row["mode"], "old_score": old["final_score"],
                                   "new_score": new["final_score"], "score_equal": old["final_score"] == new["final_score"],
                                   "all_fields_except_timestamp_equal": comparison_only(old) == comparison_only(new)})
    (records / "003_dacomp_rescore_summary.json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path("/home/katherine/dac"))
    parser.add_argument("--output", type=Path, default=Path("data/003_dacomp_rescore"))
    parser.add_argument("--records", type=Path, default=Path("records"))
    args = parser.parse_args()
    main(args.project, args.output, args.records)
