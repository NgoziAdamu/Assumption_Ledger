"""Known-answer fixtures for node schema handling and syntax/verbatim extraction."""

from pathlib import Path
import tempfile
import unittest
import duckdb
from compare_dacomp_staging import compare_table
from dacomp_sql_extract import contract_blocks, sql_structure, key_spec


class ExtractionTests(unittest.TestCase):
    def test_nested_scopes_joins_and_windows(self):
        result = sql_structure("""WITH x AS (
          SELECT a.id, count(DISTINCT b.n) n FROM staging.a a
          LEFT JOIN staging.b b ON a.id=b.a_id AND b.enabled=true
          WHERE a.id IS NOT NULL GROUP BY a.id HAVING count(*)>1
        ) SELECT DISTINCT x.id, coalesce(c.value,0) value,
          row_number() OVER(PARTITION BY x.id ORDER BY c.value DESC) rn
          FROM x JOIN staging.c c USING(id) QUALIFY rn=1""")
        root, cte = result["scopes"]
        self.assertEqual(root["joins"][0]["using_columns"], ["id"])
        self.assertEqual(cte["joins"][0]["type"], "LEFT")
        self.assertEqual(len(cte["joins"][0]["column_equality_predicates"]), 1)
        self.assertEqual(cte["group_by_expressions"], ["a.id"])
        self.assertIn("NOT a.id IS NULL", cte["filters"]["where"])
        self.assertIn("COUNT", cte["filters"]["having"])
        self.assertEqual(root["filters"]["qualify"], "rn = 1")
        self.assertEqual(len(root["row_number_windows"]), 1)
        self.assertEqual(root["row_number_windows"][0]["output_alias"], "rn")
        self.assertEqual(cte["row_number_windows"], [])
        self.assertEqual(root["coalesce"][0]["fallback_arguments"], ["0"])
        self.assertTrue(result["uses_distinct"])
        self.assertTrue(result["row_number_rank_one_filter_syntax_found"])
        self.assertEqual(result["row_number_rank_one_predicates"][0]["predicate"], "rn = 1")
        implicit = sql_structure("SELECT * FROM a,b")["scopes"][0]["joins"][0]
        self.assertEqual(implicit["type"], "CROSS (implicit/comma)")

    def test_no_syntax_is_not_a_negative_result(self):
        self.assertEqual(sql_structure("")["status"], "missing_sql")
        self.assertEqual(sql_structure("select from")["status"], "parse_failed")

    def test_contract_original_block_boundaries_and_bad_escape(self):
        source = 'models:\n  - name: wanted\n    text: "regex \\d"\n    grain: one row\n\n  - name: other\n    text: ignored\n'
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "contract.yaml"
            path.write_text(source)
            result = contract_blocks(path, "wanted")
            self.assertEqual(result["status"], "found")
            block = result["blocks"][0]
            self.assertEqual(block["original_text"], ''.join(source.splitlines(keepends=True)[1:5]))
            self.assertIn('"regex \\d"', block["original_text"])
            self.assertNotIn('ignored', block["original_text"])
            self.assertEqual(path.read_text(), source)

    def test_nonstaging_schemas_and_type_difference(self):
        spec = key_spec({"blocks": [{"specification": {"columns": [{"name": "id", "tests": ["not_null", "unique"]}]}}]}, "fixture")
        self.assertEqual(spec["columns"][0]["constraints"], ["not_null", "unique"])
        with duckdb.connect(":memory:") as pred, duckdb.connect(":memory:") as gold:
            pred.execute("CREATE SCHEMA marts; CREATE TABLE marts.fixture AS SELECT 1 AS id, 2::DOUBLE AS value")
            gold.execute("CREATE SCHEMA mart; CREATE TABLE mart.fixture AS SELECT 1 AS id, 3::INTEGER AS value")
            result = compare_table(pred, gold, "fixture", {}, {"primary_key": ["id"]}, "marts", "mart")
            self.assertEqual(result["prediction"]["row_count"], 1)
            self.assertEqual(result["mismatching_official_columns"], 1)
            self.assertEqual(result["type_differences"][0]["column"], "value")


if __name__ == "__main__":
    unittest.main()
