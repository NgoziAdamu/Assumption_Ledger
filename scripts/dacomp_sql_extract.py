"""Extract SQL syntax and verbatim contract blocks, without interpreting correctness."""

from pathlib import Path
from decimal import Decimal, InvalidOperation
import yaml
from yaml.nodes import MappingNode, SequenceNode
import sqlglot
from sqlglot import exp
from compare_dacomp_staging import plain, fingerprint


def contract_blocks(path, name):
    path = Path(path)
    text = path.read_text()
    try:
        root = yaml.compose(text)
        mode = "strict"
    except yaml.YAMLError:
        root = yaml.compose(text.replace("\\", "\\\\"))
        mode = "escape_backslashes_in_memory_for_structure_only"
    lines = text.splitlines(keepends=True)
    found = []

    def walk(node, trail):
        if isinstance(node, MappingNode):
            fields = {k.value: v for k, v in node.value}
            named = fields.get("name")
            if named and getattr(named, "value", None) == name:
                start = node.start_mark.line
                # End marks can point at the next sibling's indentation.
                end = node.end_mark.line + (1 if node.end_mark.column and lines[node.end_mark.line].strip() == "" else 0) if node.end_mark.line < len(lines) else len(lines)
                found.append({"yaml_path": trail, "start_line": start + 1, "end_line": end,
                              "original_text": "".join(lines[start:end]), "specification": plain(node)})
                return
            for key, value in node.value:
                if key.value == name and isinstance(value, MappingNode):
                    start, end = key.start_mark.line, value.end_mark.line
                    found.append({"yaml_path": trail + [key.value], "start_line": start + 1, "end_line": end,
                                  "original_text": "".join(lines[start:end]), "specification": plain(value)})
                else:
                    walk(value, trail + [key.value])
        elif isinstance(node, SequenceNode):
            for i, value in enumerate(node.value):
                walk(value, trail + [i])
    walk(root, [])
    return {"source_path": str(path), "source_sha256": fingerprint(path)["sha256"],
            "parse_mode": mode, "requested_table": name,
            "status": "found" if len(found) == 1 else "missing" if not found else "multiple_blocks",
            "blocks": found}


def key_spec(contract, table):
    specs = [b["specification"] for b in contract["blocks"]]
    spec = dict(specs[0]) if len(specs) == 1 else {}
    spec["name"] = table
    columns = spec.get("columns", [])
    if isinstance(columns, dict):
        columns = [dict(v, name=k) if isinstance(v, dict) else {"name": k} for k, v in columns.items()]
    spec["columns"] = [dict(c) for c in columns if isinstance(c, dict) and "name" in c]
    for column in spec["columns"]:
        declared = column.get("constraints") or []
        declared = [declared] if isinstance(declared, str) else list(declared)
        declared.extend(t for t in column.get("tests") or [] if isinstance(t, str) and t in ("not_null", "unique", "primary_key"))
        column["constraints"] = []
        for item in declared:
            if item not in column["constraints"]:
                column["constraints"].append(item)
    return spec


def sql_structure(sql):
    try:
        roots = [r for r in sqlglot.parse(sql, read="duckdb") if r is not None]
    except Exception as error:
        return {"status": "parse_failed", "error": str(error), "parser": sqlglot.__version__}
    if not roots:
        return {"status": "missing_sql", "parser": sqlglot.__version__}
    scopes = []
    for statement, root in enumerate(roots):
        for number, select in enumerate(root.find_all(exp.Select)):
            def local_nodes(kind):
                return [e for e in select.find_all(kind) if e.find_ancestor(exp.Select) is select]

            origin = select.args.get("from_")
            left = [origin.this.sql(dialect="duckdb")] if origin and origin.this else []
            joins = []
            for join in select.args.get("joins", []):
                on = join.args.get("on")
                equations = []
                if on is not None:
                    for eq in on.find_all(exp.EQ):
                        lhs, rhs = eq.this, eq.expression
                        if list(lhs.find_all(exp.Column)) and list(rhs.find_all(exp.Column)):
                            equations.append({"left_expression": lhs.sql(dialect="duckdb"),
                                              "right_expression": rhs.sql(dialect="duckdb"),
                                              "column_references": [c.sql(dialect="duckdb") for c in eq.find_all(exp.Column)]})
                right = join.this.sql(dialect="duckdb")
                join_type = " ".join(str(join.args.get(k) or "") for k in ("method", "side", "kind")).strip()
                if not join_type:
                    join_type = "INNER" if on is not None or join.args.get("using") else "CROSS (implicit/comma)"
                joins.append({"type": join_type, "join_sql": join.sql(dialect="duckdb"),
                              "left_relations_in_scope": list(left), "right_relation": right,
                              "right_alias": join.this.alias_or_name,
                              "on": on.sql(dialect="duckdb") if on is not None else None,
                              "using_columns": [x.sql(dialect="duckdb") for x in join.args.get("using") or []],
                              "column_equality_predicates": equations,
                              "binding_policy": "syntactic expressions; CTE/subquery names retained; no semantic column binding inferred"})
                left.append(right)
            group = select.args.get("group")
            windows = [e for e in local_nodes(exp.Window) if isinstance(e.this, exp.RowNumber)]
            scopes.append({"statement_index": statement, "select_index": number,
                           "select_sql": select.sql(dialect="duckdb"),
                           "from": origin.sql(dialect="duckdb") if origin is not None else None,
                           "joins": joins,
                           "group_by": group.sql(dialect="duckdb") if group is not None else None,
                           "group_by_expressions": [e.sql(dialect="duckdb") for e in group.expressions] if group is not None else [],
                           "group_by_all": group.args.get("all") if group is not None else False,
                           "filters": {k: select.args[k].this.sql(dialect="duckdb") if select.args.get(k) is not None else None for k in ("where", "having", "qualify")},
                           "select_distinct": select.args.get("distinct") is not None,
                           "distinct_expressions": [e.sql(dialect="duckdb") for e in local_nodes(exp.Distinct)],
                           "row_number_windows": [{"sql": e.sql(dialect="duckdb"),
                                                   "output_alias": e.parent.alias if isinstance(e.parent, exp.Alias) else None,
                                                   "partition_by": [p.sql(dialect="duckdb") for p in e.args.get("partition_by") or []],
                                                   "order_by": e.args["order"].sql(dialect="duckdb") if e.args.get("order") else None} for e in windows],
                           "coalesce": [{"sql": e.sql(dialect="duckdb"), "first_argument": e.this.sql(dialect="duckdb"),
                                         "fallback_arguments": [a.sql(dialect="duckdb") for a in e.expressions]} for e in local_nodes(exp.Coalesce)]})
    rank_aliases = {w["output_alias"].lower() for s in scopes for w in s["row_number_windows"] if w["output_alias"]}
    rank_filters = []
    def rank_reference(node):
        return isinstance(node, exp.Window) and isinstance(node.this, exp.RowNumber) or isinstance(node, exp.Column) and node.name.lower() in rank_aliases
    def numeric(node, value):
        try:
            return isinstance(node, exp.Literal) and not node.is_string and Decimal(node.this) == value
        except InvalidOperation:
            return False
    for statement, root in enumerate(roots):
        for index, select in enumerate(root.find_all(exp.Select)):
            for clause in ("where", "having", "qualify"):
                condition = select.args.get(clause)
                if condition is None:
                    continue
                for predicate in condition.find_all((exp.EQ, exp.LTE, exp.LT)):
                    left, right = predicate.this, predicate.expression
                    matched = (isinstance(predicate, exp.EQ) and ((rank_reference(left) and numeric(right, 1)) or (rank_reference(right) and numeric(left, 1)))) or (isinstance(predicate, exp.LTE) and rank_reference(left) and numeric(right, 1)) or (isinstance(predicate, exp.LT) and rank_reference(left) and numeric(right, 2))
                    if matched:
                        rank_filters.append({"statement_index": statement, "select_index": index, "clause": clause,
                                             "predicate": predicate.sql(dialect="duckdb"), "full_condition": condition.this.sql(dialect="duckdb"),
                                             "policy": "rank-one syntax only; alias matches across scopes are candidates, not proven bindings or deduplication intent"})
    return {"status": "parsed", "parser": sqlglot.__version__, "dialect": "duckdb", "scopes": scopes,
            "cte_definitions": [{"name": c.alias_or_name, "sql": c.this.sql(dialect="duckdb")} for root in roots for c in root.find_all(exp.CTE)],
            "uses_distinct": any(s["distinct_expressions"] for s in scopes),
            "uses_row_number": any(s["row_number_windows"] for s in scopes),
            "uses_coalesce": any(s["coalesce"] for s in scopes),
            "row_number_rank_one_predicates": rank_filters,
            "row_number_rank_one_filter_syntax_found": bool(rank_filters),
            "row_number_interpretation": "window expressions and filters recorded separately; use for deduplication is not asserted"}
