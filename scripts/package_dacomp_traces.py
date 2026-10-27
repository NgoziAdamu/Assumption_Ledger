"""Package verified text traces, scores and final agent code with a reproducible inventory."""

from collections import defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import tarfile


SOURCE = Path("data/dacomp_deimpl_prev")
RECORDS = Path("records")
DESTINATION = Path("traces/dacomp_deimpl_prev")
ARCHIVE = Path("traces/dacomp_deimpl_prev.tar.gz")


def summary(rows, key):
    groups = defaultdict(lambda: {"files": 0, "bytes": 0})
    for row in rows:
        group = groups[key(row)]
        group["files"] += 1
        group["bytes"] += row["bytes"]
    return dict(sorted(groups.items()))


def directory_group(row):
    parts = Path(row["path"]).parts
    if len(parts) == 1:
        return parts[0]
    if parts[0] == "analysis":
        return "/".join(parts[:2])
    if parts[1] != "20261025_de_official_batch_01":
        return "/".join(parts[:3])
    if not parts[2].startswith("impl-"):
        return "runs/20261025_de_official_batch_01/batch_metadata"
    if ".events" in parts:
        return "runs/batch/tasks/agent/.events/" + ("event_cache" if "event_cache" in parts else "events" if "events" in parts else "session_metadata")
    if "sidecar" in parts:
        return "runs/batch/tasks/agent/sidecar/" + ("sql_versions" if "sql_changes" in parts else "indices")
    if ".tmp" in parts:
        return "runs/batch/tasks/agent/workspace/.tmp"
    if len(parts) > 4 and parts[4].startswith("dacomp-de-"):
        return "runs/batch/tasks/agent/workspace/final_artifacts"
    if len(parts) > 3 and parts[3] == "agent":
        return "runs/batch/tasks/agent/history_and_metadata"
    return "runs/batch/tasks/run_metadata_and_logs"


def main():
    inventory = json.loads((RECORDS / "003_dacomp_inventory.json").read_text())
    included = [row for row in inventory if row["disposition"] == "archive"]
    for row in included:
        path = SOURCE / row["path"]
        assert not path.is_symlink()
        assert path.stat().st_size == row["bytes"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]
        assert not {"analysis", "gold", "raw_data", ".git", "event_cache", ".venv", ".agent-python"}.intersection(Path(row["path"]).parts)
        path.read_bytes().decode("utf-8")
    DESTINATION.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE / "HANDOVER.md", DESTINATION / "HANDOVER.md")
    shutil.copyfile(RECORDS / "003_dacomp_task_scores.csv", DESTINATION / "task_scores.csv")
    temporary = ARCHIVE.with_name(ARCHIVE.name + ".tmp")
    with temporary.open("xb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as zipped:
            with tarfile.open(fileobj=zipped, mode="w", format=tarfile.PAX_FORMAT) as tar:
                for row in included:
                    path = SOURCE / row["path"]
                    info = tar.gettarinfo(str(path), arcname="dacomp_deimpl_prev/" + row["path"])
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    info.mtime = 0
                    info.mode = 0o644
                    with path.open("rb") as stream:
                        tar.addfile(info, stream)
    temporary.replace(ARCHIVE)
    checked = 0
    by_path = {"dacomp_deimpl_prev/" + r["path"]: r for r in included}
    with tarfile.open(ARCHIVE, "r:gz") as tar:
        for member in tar:
            row = by_path.pop(member.name)
            assert member.isfile() and member.size == row["bytes"]
            assert hashlib.sha256(tar.extractfile(member).read()).hexdigest() == row["sha256"]
            checked += 1
    assert not by_path
    result = {"source_files": len(inventory), "source_bytes": sum(x["bytes"] for x in inventory),
              "by_subdirectory": summary(inventory, directory_group),
              "by_file_type": summary(inventory, lambda r: Path(r["path"]).suffix or "(no extension)"),
              "by_disposition": summary(inventory, lambda r: r["disposition"]),
              "archive_by_subdirectory": summary(included, directory_group),
              "archive_by_file_type": summary(included, lambda r: Path(r["path"]).suffix or "(no extension)"),
              "excluded_by_subdirectory": summary([r for r in inventory if r["disposition"] != "archive"], directory_group),
              "archive": str(ARCHIVE), "archive_bytes": ARCHIVE.stat().st_size,
              "archive_sha256": hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
              "archived_files": checked, "archived_uncompressed_bytes": sum(x["bytes"] for x in included),
              "over_50_MB": ARCHIVE.stat().st_size > 50_000_000,
              "uncompressed_handover_sha256": hashlib.sha256((DESTINATION / "HANDOVER.md").read_bytes()).hexdigest(),
              "all_members_verified_against_source_hashes": True,
              "analysis_in_archive": False, "binary_files_in_archive": False}
    (RECORDS / "003_dacomp_package_summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("archive_bytes", "archive_sha256", "archived_files", "archived_uncompressed_bytes", "over_50_MB")}, indent=2))


if __name__ == "__main__":
    main()
