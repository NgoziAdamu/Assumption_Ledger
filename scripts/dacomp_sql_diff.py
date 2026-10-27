"""Disk-backed SQL equivalent of report 004's key grouping and per-column multisets."""

from pathlib import Path
import tempfile
import duckdb
from compare_dacomp_staging import quote, key_candidates, schema, read_rows, align_and_compare


def adaptive_alignment(pred, gold, table, columns, spec, official, pred_schema, gold_schema):
    large = max(schema(pred, table, pred_schema)["row_count"], schema(gold, table, gold_schema)["row_count"]) > 100000
    if large:
        alignment, differences = sql_alignment(pred, gold, table, columns, spec, official, pred_schema, gold_schema)
    else:
        alignment, differences = align_and_compare(read_rows(pred, table, columns, pred_schema), read_rows(gold, table, columns, gold_schema), columns, spec, official)
    alignment["engine"] = "duckdb_disk_aggregation" if large else "python_row_groups"
    return alignment, differences


def sql_alignment(pred, gold, table, columns, spec, official, pred_schema, gold_schema):
    with tempfile.TemporaryDirectory(prefix="cs_diff_") as tmp:
        with duckdb.connect(str(Path(tmp) / "diff.duckdb")) as conn:
            conn.execute("SET memory_limit='768MB'; SET threads=2")
            conn.execute("SET temp_directory='" + str(Path(tmp) / "spill").replace("'", "''") + "'")
            for alias, source, schema_name in (("p", pred, pred_schema), ("g", gold, gold_schema)):
                path = source.execute("PRAGMA database_list").fetchone()[2]
                if not path:
                    raise ValueError("SQL aggregation requires file-backed read-only inputs")
                conn.execute("ATTACH '" + path.replace("'", "''") + f"' AS {alias}_source (READ_ONLY)")
                expressions = []
                for i, column in enumerate(columns):
                    raw = f"cast({quote(column)} as varchar)"
                    expressions += [f"coalesce(lower(trim({raw})),'null') AS n{i}", f"{raw} AS r{i}"]
                conn.execute(f"CREATE TABLE {alias} AS SELECT {','.join(expressions)} FROM {alias}_source.{quote(schema_name)}.{quote(table)}")
            return aggregate(conn, columns, spec, official)


def aggregate(conn, columns, spec, official):
    candidates, required_ids = key_candidates(spec, columns)
    profiles, selected = [], None
    for candidate in candidates:
        names = [f"n{columns.index(c)}" for c in candidate["columns"]]
        profile = dict(candidate)
        for side, label in (("p", "pred"), ("g", "gold")):
            count, duplicates = conn.execute(f"SELECT count(*),count(*) FILTER(WHERE n>1) FROM (SELECT {','.join(names)},count(*) n FROM {side} GROUP BY ALL)").fetchone()
            profile.update({label + "_distinct_keys": count, label + "_duplicate_key_groups": duplicates})
        profiles.append(profile)
        if selected is None:
            selected = profile
        if candidate["reason"].startswith("contract_declared") or "unique" in candidate["reason"] or "primary_key" in candidate["reason"]:
            selected = profile
            break
        if not profile["pred_duplicate_key_groups"] and not profile["gold_duplicate_key_groups"]:
            selected = profile
            break
    if selected is None:
        return {"status": "no_common_key_columns", "columns": []}, []
    if all(p["pred_duplicate_key_groups"] or p["gold_duplicate_key_groups"] for p in profiles):
        composite = next((p for p in profiles if p["reason"] == "inferred_id_date_dimension_composite"), None)
        if composite and not selected["reason"].startswith(("contract_declared", "contract_not_null_unique", "contract_unique", "contract_column_primary")):
            selected = composite
    indices = [columns.index(c) for c in selected["columns"]]
    keys = [f"n{i}" for i in indices]
    key_sql = ','.join(keys)
    for side in ("p", "g"):
        conn.execute(f"CREATE TABLE {side}k AS SELECT {key_sql},count(*) AS {side}rows FROM {side} GROUP BY ALL")
    conn.execute(f"CREATE TABLE kg AS SELECT * FROM pk FULL JOIN gk USING({key_sql})")
    stats = conn.execute("""SELECT count(*) FILTER(WHERE prows IS NOT NULL AND grows IS NULL),
      count(*) FILTER(WHERE grows IS NOT NULL AND prows IS NULL),
      count(*) FILTER(WHERE prows IS NOT NULL AND grows IS NOT NULL),
      count(*) FILTER(WHERE prows=1 AND grows=1),
      count(*) FILTER(WHERE prows IS NOT NULL AND grows IS NOT NULL AND (prows>1 OR grows>1)),
      coalesce(sum(prows) FILTER(WHERE grows IS NOT NULL AND (prows>1 OR grows>1)),0),
      coalesce(sum(grows) FILTER(WHERE prows IS NOT NULL AND (prows>1 OR grows>1)),0) FROM kg""").fetchone()
    fields = ("pred_only_keys", "gold_only_keys", "shared_keys", "shared_one_to_one_keys", "shared_nonunique_key_groups", "pred_rows_in_shared_nonunique_groups", "gold_rows_in_shared_nonunique_groups")
    alignment = {**selected, "status": "grouped_nonunique_keys" if stats[4] else "unique_shared_keys",
                 "contract_not_null_id_candidates": required_ids, "candidate_profiles": profiles,
                 **dict(zip(fields, stats))}
    for side, label in (("p", "pred"), ("g", "gold")):
        nulls = " OR ".join(f"r{i} IS NULL" for i in indices)
        empty = " OR ".join(f"n{i}=''" for i in indices)
        alignment[label + "_null_key_rows"], alignment[label + "_empty_key_rows"] = conn.execute(f"SELECT count(*) FILTER(WHERE {nulls}),count(*) FILTER(WHERE {empty}) FROM {side}").fetchone()
    if not stats[4]:
        return alignment, unique_columns(conn, columns, official, keys, selected)
    differences = []
    for i, column in enumerate(columns):
        for side in ("p", "g"):
            conn.execute(f"CREATE OR REPLACE TABLE {side}v AS SELECT {key_sql},n{i} AS v,count(*) AS n,any_value(r{i}) AS raw FROM {side} GROUP BY ALL")
        conn.execute(f"""CREATE OR REPLACE TABLE residual AS
          SELECT {','.join('coalesce(pv.'+k+',gv.'+k+') AS '+k for k in keys)},coalesce(pv.v,gv.v) AS v,
          greatest(coalesce(pv.n,0)-coalesce(gv.n,0),0) AS pn,
          greatest(coalesce(gv.n,0)-coalesce(pv.n,0),0) AS gn,
          pv.raw AS praw,gv.raw AS graw
          FROM pv FULL JOIN gv USING({key_sql},v)""")
        conn.execute(f"""CREATE OR REPLACE TABLE perkey AS SELECT {key_sql},max(prows) AS prows,max(grows) AS grows,sum(pn) AS pn,sum(gn) AS gn
          FROM residual JOIN kg USING({key_sql}) WHERE prows IS NOT NULL AND grows IS NOT NULL GROUP BY ALL""")
        exact, minimum, punmatched, gunmatched = conn.execute("""SELECT
          coalesce(sum(least(pn,gn)) FILTER(WHERE prows=1 AND grows=1),0),
          coalesce(sum(least(pn,gn)) FILTER(WHERE prows>1 OR grows>1),0),
          coalesce(sum(pn),0),coalesce(sum(gn),0) FROM perkey""").fetchone()
        examples = []
        for row in conn.execute(f"SELECT {key_sql},prows,grows FROM perkey WHERE pn>0 AND gn>0 ORDER BY {key_sql} LIMIT 3").fetchall():
            values, pr, gr = row[:-2], row[-2], row[-1]
            condition = ' AND '.join(f"{k}=?" for k in keys)
            key = dict(zip(selected["columns"], values))
            if pr == gr == 1:
                pvalue = conn.execute(f"SELECT praw,v FROM residual WHERE {condition} AND pn>0", values).fetchone()
                gvalue = conn.execute(f"SELECT graw,v FROM residual WHERE {condition} AND gn>0", values).fetchone()
                examples.append({"kind": "one_to_one", "key": key, "prediction_value": pvalue[0], "gold_value": gvalue[0], "prediction_normalized": pvalue[1], "gold_normalized": gvalue[1]})
            else:
                def residuals(prefix):
                    return [{"value": r[0], "normalized": r[1], "rows": r[2]} for r in conn.execute(f"SELECT {prefix}raw,v,{prefix}n FROM residual WHERE {condition} AND {prefix}n>0 ORDER BY v LIMIT 3", values).fetchall()]
                pn, gn = conn.execute(f"SELECT pn,gn FROM perkey WHERE {condition}", values).fetchone()
                examples.append({"kind": "nonunique_key_multisets_not_a_row_pair", "key": key,
                                 "prediction_unmatched_values": residuals("p"), "gold_unmatched_values": residuals("g"), "minimum_different_value_pairs": min(pn, gn)})
        differences.append({"column": column, "included_in_official_comparison": column in official,
                            "one_to_one_mismatch_rows": exact, "nonunique_key_minimum_value_mismatch_pairs": minimum,
                            "mismatch_rows_or_minimum_pairs": exact + minimum,
                            "pred_unmatched_value_occurrences": punmatched, "gold_unmatched_value_occurrences": gunmatched,
                            "count_semantics": "minimum_value_mismatch_pairs" if stats[4] else "exact_one_to_one_rows", "examples": examples})
    return alignment, differences


def unique_columns(conn, columns, official, keys, selection):
    expressions = []
    for i in range(len(columns)):
        expressions += [f"p.n{i} AS pn{i}", f"p.r{i} AS pr{i}", f"g.n{i} AS gn{i}", f"g.r{i} AS gr{i}"]
    conn.execute(f"CREATE TABLE aligned AS SELECT {','.join(expressions)} FROM p JOIN g USING({','.join(keys)})")
    counts = conn.execute('SELECT ' + ','.join(f"coalesce(sum(cast(pn{i}<>gn{i} AS BIGINT)),0)" for i in range(len(columns))) + ' FROM aligned').fetchone()
    differences = []
    key_aliases = ["p" + k for k in keys]
    for i, (column, count) in enumerate(zip(columns, counts)):
        examples = []
        if count:
            sql = f"SELECT {','.join(key_aliases)},pr{i},gr{i},pn{i},gn{i} FROM aligned WHERE pn{i}<>gn{i} ORDER BY {','.join(key_aliases)} LIMIT 3"
            for row in conn.execute(sql).fetchall():
                examples.append({"kind": "one_to_one", "key": dict(zip(selection["columns"], row[:-4])),
                                 "prediction_value": row[-4], "gold_value": row[-3], "prediction_normalized": row[-2], "gold_normalized": row[-1]})
        differences.append({"column": column, "included_in_official_comparison": column in official,
                            "one_to_one_mismatch_rows": count, "nonunique_key_minimum_value_mismatch_pairs": 0,
                            "mismatch_rows_or_minimum_pairs": count, "pred_unmatched_value_occurrences": count,
                            "gold_unmatched_value_occurrences": count, "count_semantics": "exact_one_to_one_rows", "examples": examples})
    return differences
