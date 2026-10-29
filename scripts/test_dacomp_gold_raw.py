"""Content fingerprint framing and literal B7 graph checks for task 015."""

import unittest

import duckdb

from check_dacomp_gold_raw import descendants, sorted_hash


class GoldRawTests(unittest.TestCase):
    def setUp(self):
        self.conn = duckdb.connect(':memory:')
        self.conn.execute('CREATE SCHEMA raw')

    def tearDown(self):
        self.conn.close()

    def test_sorting_and_duplicate_multiplicity(self):
        self.conn.execute("CREATE TABLE raw.a AS SELECT * FROM (VALUES (2,'x'),(1,'y'),(1,'y')) v(id,s)")
        self.conn.execute('CREATE TABLE raw.b AS SELECT * FROM raw.a ORDER BY id DESC')
        self.assertEqual(sorted_hash(self.conn, 'a')['sha256'], sorted_hash(self.conn, 'b')['sha256'])
        self.conn.execute('CREATE TABLE raw.c AS SELECT DISTINCT * FROM raw.a')
        self.assertNotEqual(sorted_hash(self.conn, 'a')['sha256'], sorted_hash(self.conn, 'c')['sha256'])

    def test_null_empty_case_whitespace_and_framing(self):
        self.conn.execute('CREATE TABLE raw.a (s VARCHAR,t VARCHAR)')
        self.conn.execute('CREATE TABLE raw.b (s VARCHAR,t VARCHAR)')
        for left, right in ((None, ''), ('a', 'A'), (' a', 'a')):
            self.conn.execute('DELETE FROM raw.a; DELETE FROM raw.b')
            self.conn.execute('INSERT INTO raw.a VALUES (?,?)', [left, 'x'])
            self.conn.execute('INSERT INTO raw.b VALUES (?,?)', [right, 'x'])
            self.assertNotEqual(sorted_hash(self.conn, 'a')['sha256'], sorted_hash(self.conn, 'b')['sha256'])
        self.conn.execute('DELETE FROM raw.a; DELETE FROM raw.b')
        self.conn.execute("INSERT INTO raw.a VALUES ('a|b','c'); INSERT INTO raw.b VALUES ('a','b|c')")
        self.assertNotEqual(sorted_hash(self.conn, 'a')['sha256'], sorted_hash(self.conn, 'b')['sha256'])

    def test_literal_transitive_graph_with_cycle(self):
        graph = {'raw.x': {'staging.a'}, 'staging.a': {'intermediate.b'}, 'intermediate.b': {'staging.a', 'marts.c'}}
        pending = {'marts.c': {'task': 'impl-test', 'layer': 'marts', 'table': 'c'},
                   'staging.a': {'task': 'impl-test', 'layer': 'staging', 'table': 'a'}}
        rows = descendants(graph, 'raw.x', pending)
        self.assertEqual({r['table']: r['hops'] for r in rows}, {'a': 1, 'c': 3})
        self.assertEqual(next(r for r in rows if r['table'] == 'c')['one_shortest_path'], ['raw.x', 'staging.a', 'intermediate.b', 'marts.c'])


if __name__ == '__main__':
    unittest.main()
