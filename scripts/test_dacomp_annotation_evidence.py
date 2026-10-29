"""Check that annotation evidence keeps raw text and does not invent duplicate-key pairs."""

from pathlib import Path
import tempfile
import unittest

import duckdb

from dacomp_annotation_evidence import Evidence


class EvidenceTests(unittest.TestCase):
    def test_raw_format_sample_and_numeric_clearance(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name,rows in [('p',"(' A ','1573.0'),('p','9')"),('g',"('a','1573'),('g','9')")]:
                with duckdb.connect(str(root/(name+'.duckdb'))) as con:con.execute('CREATE SCHEMA staging; CREATE TABLE staging.x(id VARCHAR,v VARCHAR); INSERT INTO staging.x VALUES '+rows)
            basis={'actual_schema':'staging','table':'x','comparison_columns':['id','v'],'key_columns':['id'],
                'prediction_database':str(root/'p.duckdb'),'gold_database':str(root/'g.duckdb'),'prediction_rows':2,'gold_rows':2,
                'key_statistics':{'pred_only_keys':1,'gold_only_keys':1,'shared_keys':1}}
            with Evidence(basis,root/'work') as e:
                counts,samples=e.value_examples('v')
                self.assertEqual(counts['mismatch_rows_or_minimum_pairs'],1)
                self.assertEqual(samples[0]['agent_value'],'1573.0');self.assertEqual(samples[0]['gold_value'],'1573')
                self.assertEqual(samples[0]['agent_key_raw_text']['id'],' A ')
                self.assertEqual(e.make_histogram('v',1)['mismatch_rows_or_minimum_pairs'],0)
                self.assertEqual(e.exclusive_examples()['prediction_only'][0]['key_raw_text']['id'],'p')

    def test_duplicate_key_values_are_groups(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name,rows in [('p',"('a','1'),('a','3')"),('g',"('a','1'),('a','4')")]:
                with duckdb.connect(str(root/(name+'.duckdb'))) as con:con.execute('CREATE SCHEMA staging; CREATE TABLE staging.x(id VARCHAR,v VARCHAR); INSERT INTO staging.x VALUES '+rows)
            basis={'actual_schema':'staging','table':'x','comparison_columns':['v'],'key_columns':['id'],
                'prediction_database':str(root/'p.duckdb'),'gold_database':str(root/'g.duckdb'),'prediction_rows':2,'gold_rows':2,
                'key_statistics':{'pred_only_keys':0,'gold_only_keys':0,'shared_keys':1}}
            with Evidence(basis,root/'work') as e:
                counts,samples=e.value_examples('v')
                self.assertEqual(counts['mismatch_rows_or_minimum_pairs'],1)
                self.assertEqual(samples[0]['kind'],'duplicate_key_group_not_a_unique_row_pair')
                self.assertNotIn('agent_value',samples[0])


if __name__=='__main__':unittest.main()
