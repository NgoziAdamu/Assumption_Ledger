"""Known-answer checks for target mapping and denominator arithmetic in task 009."""

from pathlib import Path
import tempfile
import unittest
import sys

import duckdb

from complete_dacomp_comparisons import ROOT,SUITE,mapped_config,selection
from reconcile_dacomp_scope import partition


class CompletionTests(unittest.TestCase):
    def test_selection_uses_archived_cs_flags(self):
        rows=selection()
        self.assertEqual(len(rows),21)
        self.assertTrue(all(r['eligible'] and r['archived_cs_match'] is False for r in rows))
        pendo=[r for r in rows if r['number']==2]
        self.assertEqual(len(pendo),18)
        self.assertTrue(all(r['archived_gold_execution'] is False and r['table']=='pendo__'+r['scoring_table'] for r in pendo))

    def test_mapping_does_not_mutate_input_or_columns(self):
        cfg={'layers':{'marts':{'tables':{'account':{'compare_cols':['id'],'weight':2}}}}}
        result=mapped_config(cfg,2)
        self.assertIn('account',cfg['layers']['marts']['tables'])
        self.assertEqual(result['layers']['marts']['tables'],{'pendo__account':{'compare_cols':['id'],'weight':2,'sql_name':'account'}})
        self.assertEqual(mapped_config(cfg,10),cfg)

    def test_partition_counts_overlap_and_excludes_replay_pass(self):
        rows=[{'current_pred_execution':False,'gold_exists':False,'bilateral_comparable':False,'replay_l0_match':False,'comparable_failed':False,'whole_level':None},
            {'current_pred_execution':True,'gold_exists':True,'bilateral_comparable':True,'replay_l0_match':True,'comparable_failed':False,'whole_level':'L0'},
            {'current_pred_execution':True,'gold_exists':True,'bilateral_comparable':True,'replay_l0_match':False,'comparable_failed':True,'whole_level':'L2'},
            {'current_pred_execution':True,'gold_exists':True,'bilateral_comparable':True,'replay_l0_match':False,'comparable_failed':True,'whole_level':'仍不匹配'}]
        result=partition(rows)
        self.assertEqual(result['unavailable_union'],1)
        self.assertEqual(result['execution_failed_and_gold_missing'],1)
        self.assertEqual(result['comparable_failed_excluding_replay_pass'],2)
        self.assertEqual(result['format_difference'],1)
        self.assertEqual(result['pending_annotation'],1)

    def test_official_node_builder_with_explicit_filename_adapter(self):
        sys.path.insert(0,str(SUITE))
        from utils import CSEvaluator,CoreAccuracyEvaluator
        parent=ROOT/'data/009_test_scratch';parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as temp:
            root=Path(temp);gold=root/'gold';pred=root/'pred';gold.mkdir();(pred/'sql/marts').mkdir(parents=True)
            (pred/'sql/marts/account.sql').write_text('SELECT id FROM staging.upstream')
            database=gold/'fixture.duckdb'
            with duckdb.connect(str(database)) as connection:
                connection.execute('CREATE SCHEMA staging; CREATE SCHEMA marts; CREATE TABLE staging.upstream AS SELECT 7 AS id; CREATE TABLE marts.pendo__account AS SELECT 7 AS id')
            cfg={'database_file':'fixture.duckdb','layers':{'marts':{'tables':{'account':{'weight':1,'compare_cols':['id']}}}}}
            mapped=mapped_config(cfg,2);evaluator=CSEvaluator(pred,gold,mapped,'fixture.duckdb')
            private=root/'private.duckdb'
            import shutil
            shutil.copyfile(database,private)
            with duckdb.connect(str(private)) as connection:
                self.assertTrue(evaluator._build_pred_table(connection,'marts','pendo__account','marts'))
            self.assertTrue(CoreAccuracyEvaluator(private,database,mapped).compare_table('marts','pendo__account'))
            self.assertFalse(CoreAccuracyEvaluator(private,database,cfg).compare_table('marts','account'))


if __name__=='__main__':unittest.main()
