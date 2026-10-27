"""Small known-answer fixtures for the mechanical comparison, using in-memory databases."""

import unittest

import duckdb

from compare_dacomp_staging import compare_table


class MechanicalComparisonTests(unittest.TestCase):
    def setUp(self):
        self.pred = duckdb.connect(":memory:")
        self.gold = duckdb.connect(":memory:")
        self.pred.execute("CREATE SCHEMA staging")
        self.gold.execute("CREATE SCHEMA staging")

    def tearDown(self):
        self.pred.close()
        self.gold.close()

    def compare(self, columns):
        return compare_table(self.pred, self.gold, "fixture", {"compare_cols": columns},
                             {"name": "fixture", "primary_key": ["id"]})

    def test_no_rounding_or_global_time_exclusion(self):
        for connection in (self.pred, self.gold):
            connection.execute("CREATE TABLE staging.fixture(id VARCHAR, value DECIMAL(10,3), created_at TIMESTAMP)")
        self.pred.execute("INSERT INTO staging.fixture VALUES (' A ', 1.234, '2020-01-01')")
        self.gold.execute("INSERT INTO staging.fixture VALUES ('a', 1.233, '2020-01-02')")
        result = self.compare(["id", "value", "created_at"])
        self.assertEqual(result["alignment"]["shared_keys"], 1)
        self.assertEqual(result["mismatching_official_columns"], 2)
        self.assertEqual(result["mismatching_all_common_columns"], 2)

    def test_duplicate_keys_use_multisets_not_cartesian_join(self):
        for connection in (self.pred, self.gold):
            connection.execute("CREATE TABLE staging.fixture(id VARCHAR, value VARCHAR)")
        self.pred.execute("INSERT INTO staging.fixture VALUES ('a','x'), ('a','y'), ('b','z')")
        self.gold.execute("INSERT INTO staging.fixture VALUES ('a','x'), ('a','w'), ('b','z')")
        result = self.compare(["id", "value"])
        self.assertEqual(result["alignment"]["shared_nonunique_key_groups"], 1)
        field = next(x for x in result["column_differences"] if x["column"] == "value")
        self.assertEqual(field["mismatch_rows_or_minimum_pairs"], 1)
        self.assertEqual(field["one_to_one_mismatch_rows"], 0)
        self.assertEqual(field["examples"][0]["kind"], "nonunique_key_multisets_not_a_row_pair")

    def test_null_and_empty_keys_are_not_dropped(self):
        for connection in (self.pred, self.gold):
            connection.execute("CREATE TABLE staging.fixture(id VARCHAR, value INTEGER)")
        self.pred.execute("INSERT INTO staging.fixture VALUES (NULL,1), ('',2), ('p',3)")
        self.gold.execute("INSERT INTO staging.fixture VALUES (NULL,1), ('',9), ('g',4)")
        result = self.compare(["id", "value"])
        self.assertEqual(result["alignment"]["shared_keys"], 2)
        self.assertEqual(result["alignment"]["pred_only_keys"], 1)
        self.assertEqual(result["alignment"]["gold_only_keys"], 1)
        self.assertEqual(result["alignment"]["pred_null_key_rows"], 1)
        self.assertEqual(result["alignment"]["pred_empty_key_rows"], 1)

    def test_missing_table_is_unknown_not_zero(self):
        self.pred.execute("CREATE TABLE staging.fixture AS SELECT 1 AS id, 2 AS value")
        result = self.compare(["id", "value"])
        self.assertIsNone(result["gold"]["row_count"])
        self.assertIsNone(result["mismatching_official_columns"])

    def test_case_insensitive_compare_cols(self):
        self.pred.execute('CREATE TABLE staging.fixture AS SELECT 1 AS "ID", 2 AS "VALUE"')
        self.gold.execute("CREATE TABLE staging.fixture AS SELECT 1 AS id, 3 AS value")
        result = self.compare(["id", "value"])
        self.assertEqual(result["mismatching_official_columns"], 1)
        self.assertEqual(len(result["case_only_column_name_differences"]), 2)

    def test_columns_outside_compare_cols_still_have_separate_details(self):
        self.pred.execute("CREATE TABLE staging.fixture AS SELECT 1 AS id, 2 AS value, 'first' AS extra")
        self.gold.execute("CREATE TABLE staging.fixture AS SELECT 1 AS id, 2 AS value, 'second' AS extra")
        result = self.compare(["id", "value"])
        self.assertEqual(result["mismatching_official_columns"], 0)
        self.assertEqual(result["mismatching_all_common_columns"], 1)

    def test_numeric_string_formats_and_types_remain_distinct(self):
        self.pred.execute("CREATE TABLE staging.fixture(id INTEGER, value DOUBLE)")
        self.gold.execute("CREATE TABLE staging.fixture(id INTEGER, value DECIMAL(8,2))")
        self.pred.execute("INSERT INTO staging.fixture VALUES (1, 1.0)")
        self.gold.execute("INSERT INTO staging.fixture VALUES (1, 1.00)")
        result = self.compare(["id", "value"])
        self.assertEqual(len(result["type_differences"]), 1)
        self.assertEqual(result["mismatching_official_columns"], 1)

    def test_duplicate_multiplicity_is_separate_from_value_disagreement(self):
        for connection in (self.pred, self.gold):
            connection.execute("CREATE TABLE staging.fixture(id VARCHAR, value VARCHAR)")
        self.pred.execute("INSERT INTO staging.fixture VALUES ('a','x'), ('a','x')")
        self.gold.execute("INSERT INTO staging.fixture VALUES ('a','x')")
        result = self.compare(["id", "value"])
        self.assertEqual(result["row_count_delta_pred_minus_gold"], 1)
        field = next(x for x in result["column_differences"] if x["column"] == "value")
        self.assertEqual(field["mismatch_rows_or_minimum_pairs"], 0)
        self.assertEqual(field["pred_unmatched_value_occurrences"], 1)
        self.assertEqual(field["gold_unmatched_value_occurrences"], 0)

    def test_only_three_examples_but_full_mismatch_count(self):
        for connection in (self.pred, self.gold):
            connection.execute("CREATE TABLE staging.fixture(id INTEGER, value INTEGER)")
        self.pred.execute("INSERT INTO staging.fixture SELECT i, i FROM range(5) t(i)")
        self.gold.execute("INSERT INTO staging.fixture SELECT i, i+1 FROM range(5) t(i)")
        result = self.compare(["id", "value"])
        field = next(x for x in result["column_differences"] if x["column"] == "value")
        self.assertEqual(field["mismatch_rows_or_minimum_pairs"], 5)
        self.assertEqual(len(field["examples"]), 3)

    def test_empty_prediction_keeps_gold_key_counts(self):
        for connection in (self.pred, self.gold):
            connection.execute("CREATE TABLE staging.fixture(id INTEGER, value INTEGER)")
        self.gold.execute("INSERT INTO staging.fixture VALUES (1, 5), (2, 6)")
        result = self.compare(["id", "value"])
        self.assertEqual(result["prediction"]["row_count"], 0)
        self.assertEqual(result["alignment"]["gold_only_keys"], 2)
        self.assertEqual(result["alignment"]["shared_keys"], 0)


if __name__ == "__main__":
    unittest.main()
