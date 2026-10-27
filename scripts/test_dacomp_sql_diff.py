"""Check the disk-backed engine against all known-answer report 004 fixtures."""

from pathlib import Path
import tempfile
import unittest
import duckdb
from test_compare_dacomp_staging import MechanicalComparisonTests
from compare_dacomp_staging import compare_table
from dacomp_sql_diff import sql_alignment


class SQLComparisonTests(MechanicalComparisonTests):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.pred = duckdb.connect(str(root / "pred.duckdb"))
        self.gold = duckdb.connect(str(root / "gold.duckdb"))
        self.pred.execute("CREATE SCHEMA staging")
        self.gold.execute("CREATE SCHEMA staging")

    def tearDown(self):
        super().tearDown()
        self.temporary.cleanup()

    def compare(self, columns):
        expected = super().compare(columns)
        # Close writers so the disk-backed engine can attach both inputs READ_ONLY.
        pred_path = self.pred.execute("PRAGMA database_list").fetchone()[2]
        gold_path = self.gold.execute("PRAGMA database_list").fetchone()[2]
        self.pred.close(); self.gold.close()
        self.pred = duckdb.connect(pred_path, read_only=True)
        self.gold = duckdb.connect(gold_path, read_only=True)
        result = compare_table(self.pred, self.gold, "fixture", {"compare_cols": columns},
                               {"name": "fixture", "primary_key": ["id"]}, alignment_engine=sql_alignment)
        self.assertEqual(result, expected)
        return result


if __name__ == "__main__":
    unittest.main()
