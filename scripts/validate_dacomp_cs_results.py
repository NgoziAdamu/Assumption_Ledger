"""Validate selection, syntax coverage, archived sources, and independent SQL counts."""

from collections import Counter
import json
from pathlib import Path
import subprocess
import sys

import duckdb
import sqlglot
from sqlglot import exp
import yaml

from compare_dacomp_cs_nodes import WORKSPACE, PROJECT, SUITE, PYTHON, inputs, targets, save
from compare_dacomp_staging import quote


def full_official(number):
    existing = WORKSPACE / f"data/005_full_cs_validation_v2/impl-{number:03d}/full_official_cs.json"
    final = WORKSPACE / f"data/005_full_cs_validation_final/impl-{number:03d}/full_official_cs.json"
    if final.exists():
        existing = final
    if existing.exists() and json.loads(existing.read_text())["layers"]:
        result = json.loads(existing.read_text())
        command = json.loads((existing.parent / "command.json").read_text())
    else:
        sys.path.insert(0, str(PROJECT / "src"))
        from safe_env import scrubbed_env
        from review_de_pilots import sandbox_command
        case = WORKSPACE / f"data/005_full_cs_validation_final/impl-{number:03d}"
        case.mkdir(parents=True, exist_ok=False)
        args = [str(PYTHON), str(WORKSPACE / "scripts/compare_dacomp_cs_nodes.py"), "--validate-official", str(number), "--case", str(case)]
        command = sandbox_command(case, args)
        position = command.index("--bind")
        command[position:position] = ["--ro-bind", str(WORKSPACE), str(WORKSPACE)]
        environment = scrubbed_env()
        environment.update(PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", PYTHONPATH=str(WORKSPACE / "data/005_tools"))
        with (case / "execution.log").open("w") as stream:
            completed = subprocess.run(command, env=environment, stdout=stream, stderr=subprocess.STDOUT, timeout=3600)
        command = {"command": command, "returncode": completed.returncode}
        save(case / "command.json", command)
        if completed.returncode:
            raise RuntimeError(f"Full official validation failed: {case}")
        result = json.loads((case / "full_official_cs.json").read_text())
    save(WORKSPACE / f"records/005_cs_full_official_impl-{number:03d}.json", {**result, "execution": command})
    return result


def independent_column_count(detail, table, column):
    """SQL aggregation check, independent of Python row grouping/multiset code."""
    def norm(alias, name):
        return f"coalesce(lower(trim(cast({alias}.{quote(name)} as varchar))), 'null')"
    keys = table["alignment"]["columns"]
    aliases = [f"k{i}" for i in range(len(keys))]
    schema = quote(table["actual_schema"])
    relation = f"{schema}.{quote(table['table'])}"
    def side(alias, catalog):
        expressions = [f"{norm(alias, k)} AS {a}" for k, a in zip(keys, aliases)]
        expressions.append(f"{norm(alias, column)} AS v")
        return f"SELECT {','.join(expressions)},count(*) AS n FROM {catalog}.{relation} {alias} GROUP BY ALL"
    sql = f"""WITH p AS ({side('p', 'prediction')}), g AS ({side('g', 'gold')}),
      residual AS (SELECT {','.join('coalesce(p.'+a+',g.'+a+') AS '+a for a in aliases)},
        greatest(coalesce(p.n,0)-coalesce(g.n,0),0) AS pn,
        greatest(coalesce(g.n,0)-coalesce(p.n,0),0) AS gn
        FROM p FULL OUTER JOIN g USING ({','.join(aliases+['v'])})),
      per_key AS (SELECT {','.join(aliases)},sum(pn) AS pn,sum(gn) AS gn FROM residual GROUP BY ALL)
      SELECT coalesce(sum(least(pn,gn)),0) FROM per_key"""
    with duckdb.connect(":memory:") as conn:
        for alias, path in (("prediction", detail["private_node_results"]), ("gold", detail["gold_database"])):
            conn.execute("ATTACH '" + str(path).replace("'", "''") + f"' AS {alias} (READ_ONLY)")
        actual = int(conn.execute(sql).fetchone()[0])
    expected = next(c["mismatch_rows_or_minimum_pairs"] for c in table["column_differences"] if c["column"] == column)
    return {"task": detail["task"], "table": table["table"], "column": column,
            "alignment_status": table["alignment"]["status"], "sql": sql,
            "independent_sql_count": actual, "reported_count": expected, "equal": actual == expected}


def main():
    overview = json.loads((WORKSPACE / "records/005_cs_overview.json").read_text())
    configs = yaml.safe_load((SUITE / "evaluation_config_compare.yaml").read_text())["examples"]
    details = [json.loads(p.read_text()) for p in sorted((WORKSPACE / "records").glob("005_cs_impl-*.json"))]
    actual = {(d["task"], t["layer"], t["table"]) for d in details for t in d["tables"]}
    expected, selection = set(), []
    for n in range(1, 31):
        info = inputs(n, configs)
        score = json.loads(info["score"].read_text())
        expected.update((info["short"], t["layer"], t["table"]) for t in targets(info))
        selection.append({"task": info["short"], "score_path": str(info["score"]), "compatibility": n in (13, 19, 22),
                          "layer_results": score["partial_evaluation"]["layer_results"]})
    save(WORKSPACE / "records/005_cs_selection.json", selection)
    failures = []
    if actual != expected or len(actual) != overview["failed_nodes"]:
        failures.append("Final CS target coverage mismatch")
    blocks, joins, sql_files = 0, 0, 0
    for d in details:
        for t in d["tables"]:
            if t["archived_gold_execution"] != t["gold"]["exists"]:
                failures.append(f"Gold availability differs: {d['task']} {t['table']}")
            agent = t["agent_sql"]
            for path in agent["used_source_paths"]:
                sql_files += 1
                if Path(path).read_text() != agent["raw_text"]:
                    failures.append(f"Source SQL differs: {path}")
            structure = agent["structure"]
            if structure["status"] == "parsed":
                trees = sqlglot.parse(agent["raw_text"], read="duckdb")
                count = sum(len(list(tree.find_all(exp.Join))) for tree in trees)
                joins += count
                if count != sum(len(s["joins"]) for s in structure["scopes"]):
                    failures.append(f"Join coverage differs: {d['task']} {t['table']}")
            contract = t["contract"]
            source = Path(contract["source_path"]).read_text().splitlines(keepends=True)
            for block in contract["blocks"]:
                blocks += 1
                if block["original_text"] != ''.join(source[block["start_line"]-1:block["end_line"]]):
                    failures.append(f"Contract excerpt differs: {d['task']} {t['table']}")
    baseline = json.loads((WORKSPACE / "data/005_cs_work/input_before.json").read_text())
    prior004 = json.loads((WORKSPACE / "records/004_staging_input_integrity.json").read_text())["after"]
    prior003 = {str(PROJECT / x["path"]): x for x in json.loads((WORKSPACE / "records/003_dacomp_inventory.json").read_text())}
    baseline_counts = Counter()
    for path, current in baseline.items():
        if path in prior004:
            baseline_counts["prior004_checked"] += 1
            if current["sha256"] != prior004[path]["sha256"]:
                failures.append(f"Prior 004 input changed: {path}")
        if path in prior003:
            baseline_counts["prior003_archive_checked"] += 1
            if current["sha256"] != prior003[path]["sha256"]:
                failures.append(f"Prior 003 archived input changed: {path}")
    full_checks = []
    for n in (21, 13, 22):
        full = full_official(n)
        d = next(d for d in details if d["task"] == f"impl-{n:03d}")
        mapping = {l["layer_name"]: l for l in full["layers"]}
        for t in d["tables"]:
            layer = mapping[t["layer"]]
            identical = (layer["comparison_results"][t["table"]] == t["official_current_match"] and
                         layer["pred_execution"][t["table"]] == t["current_pred_execution"] and
                         layer["gold_execution"][t["table"]] == t["gold"]["exists"])
            full_checks.append({"task": d["task"], "table": t["table"], "equal": identical})
            if not identical:
                failures.append(f"Full official flow differs: {d['task']} {t['table']}")
    independent, used = [], set()
    for status in ("unique_shared_keys", "grouped_nonunique_keys"):
        for d in details:
            if sum(c["alignment_status"] == status for c in independent) >= 3:
                break
            for t in d["tables"]:
                columns = [c for c in t["column_differences"] if c["included_in_official_comparison"] and c["mismatch_rows_or_minimum_pairs"] > 0]
                if t["alignment"]["status"] != status or not columns or d["task"] in used:
                    continue
                check = independent_column_count(d, t, columns[0]["column"])
                independent.append(check); used.add(d["task"])
                if not check["equal"]:
                    failures.append(f"Independent SQL count differs: {d['task']} {t['table']}")
                break
    result = {"failures": failures, "expected_failed_nodes": len(expected), "actual_failed_nodes": len(actual),
              "sql_source_texts_checked": sql_files, "verbatim_contract_blocks_checked": blocks,
              "join_nodes_checked": joins, "prior_input_baselines": dict(baseline_counts),
              "full_official_node_checks": full_checks, "independent_column_checks": independent}
    save(WORKSPACE / "records/005_cs_validation.json", result)
    print(json.dumps({k:v for k,v in result.items() if k not in ("independent_column_checks", "full_official_node_checks")}, ensure_ascii=False), flush=True)
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
