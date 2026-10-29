"""Read-only key/value evidence for task 012; no node SQL execution."""

from contextlib import AbstractContextManager
from pathlib import Path
import tempfile

import duckdb

from compare_dacomp_staging import quote
from dacomp_tolerance import udf_forms


def norm(expression):
    return "coalesce(lower(trim("+expression+")),'null')"


class Evidence(AbstractContextManager):
    def __init__(self,basis,work):
        work.mkdir(parents=True,exist_ok=True)
        self.temporary=tempfile.TemporaryDirectory(prefix='evidence_',dir=work)
        self.connection=duckdb.connect(str(Path(self.temporary.name)/'comparison.duckdb'))
        self.connection.execute("SET memory_limit='768MB'; SET threads=2")
        self.connection.execute("SET temp_directory='"+str(Path(self.temporary.name)/'spill').replace("'","''")+"'")
        self.connection.create_function('annotation_forms',udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}))
        self.basis=basis;self.columns=list(basis['comparison_columns']);self.keys=list(basis['key_columns'])
        self.names=list(dict.fromkeys(self.keys+self.columns));self.types={}
        relation=quote(basis['actual_schema'])+'.'+quote(basis['table'])
        for side,label in [('p','prediction_database'),('g','gold_database')]:
            self.connection.execute("ATTACH '"+str(basis[label]).replace("'","''")+f"' AS {side}input (READ_ONLY)")
            self.types[side]={r[0]:r[1] for r in self.connection.execute(f'DESCRIBE SELECT * FROM {side}input.{relation}').fetchall()}
            raw={name:'cast('+quote(name)+' AS VARCHAR)' for name in self.names}
            select='list_value('+','.join(norm(raw[k]) for k in self.keys)+') AS key0,'
            select+='list_value('+','.join(raw[k] for k in self.keys)+') AS key_raw,'
            select+=','.join(raw[name]+f' AS c{i}' for i,name in enumerate(self.names))
            self.connection.execute(f'CREATE TABLE {side}0 AS SELECT {select} FROM {side}input.{relation}')
            self.connection.execute(f'CREATE TABLE {side}k AS SELECT key0,any_value(key_raw) key_raw,count(*) n FROM {side}0 GROUP BY key0')
        self.connection.execute('CREATE TABLE kg AS SELECT key0,pk.n pn,gk.n gn FROM pk FULL JOIN gk USING(key0)')
        p,g=self.connection.execute('SELECT (SELECT count(*) FROM p0),(SELECT count(*) FROM g0)').fetchone()
        self.row_counts={'prediction_rows':p,'gold_rows':g,'row_delta':p-g}
        assert p==basis['prediction_rows'] and g==basis['gold_rows'],(basis['table'],'row counts',p,g)
        row=self.connection.execute('''SELECT count(*) FILTER(WHERE pn IS NOT NULL AND gn IS NULL),
            count(*) FILTER(WHERE pn IS NULL AND gn IS NOT NULL),count(*) FILTER(WHERE pn IS NOT NULL AND gn IS NOT NULL)
            FROM kg''').fetchone()
        self.key_counts=dict(zip(['pred_only_keys','gold_only_keys','shared_keys'],row))
        for name,count in self.key_counts.items():assert count==basis['key_statistics'][name],(basis['table'],name,count,basis['key_statistics'][name])

    def __exit__(self,*args):
        self.connection.close();self.temporary.cleanup()

    def exclusive_examples(self,limit=10):
        result={}
        for side,other,label in [('p','g','prediction_only'),('g','p','gold_only')]:
            rows=self.connection.execute(f'SELECT a.key0,a.key_raw,a.n FROM {side}k a ANTI JOIN {other}k b USING(key0) ORDER BY a.key0 LIMIT {limit}').fetchall()
            result[label]=[{'key_normalized':dict(zip(self.keys,k)),'key_raw_text':dict(zip(self.keys,raw)),'rows_with_key':n} for k,raw,n in rows]
        return result

    def make_histogram(self,column,level):
        i=self.names.index(column)
        if level:
            self.connection.execute(f'CREATE OR REPLACE TABLE dictionary AS SELECT raw,annotation_forms(raw) mapped FROM (SELECT {norm(f"c{i}")} raw FROM p0 UNION SELECT {norm(f"c{i}")} raw FROM g0)')
        for side in ('p','g'):
            raw=norm(f'c{i}')
            value=f'dictionary.mapped.l{level}' if level else raw
            join=f' JOIN dictionary ON {raw}=dictionary.raw' if level else ''
            self.connection.execute(f'CREATE OR REPLACE TABLE {side}v AS SELECT key0,{value} v,count(*) n FROM {side}0{join} GROUP BY ALL')
        self.connection.execute('''CREATE OR REPLACE TABLE residual AS SELECT key0,v,
            greatest(coalesce(pv.n,0)-coalesce(gv.n,0),0) pu,
            greatest(coalesce(gv.n,0)-coalesce(pv.n,0),0) gu
            FROM pv FULL JOIN gv USING(key0,v)''')
        self.connection.execute('''CREATE OR REPLACE TABLE perkey AS SELECT key0,max(pn) pn,max(gn) gn,sum(pu) pu,sum(gu) gu
            FROM residual JOIN kg USING(key0) WHERE pn IS NOT NULL AND gn IS NOT NULL GROUP BY key0''')
        mismatch,pu,gu=self.connection.execute('SELECT coalesce(sum(least(pu,gu)),0),coalesce(sum(pu),0),coalesce(sum(gu),0) FROM perkey').fetchone()
        return {'mismatch_rows_or_minimum_pairs':mismatch,'pred_unmatched_value_occurrences':pu,'gold_unmatched_value_occurrences':gu}

    def value_examples(self,column,level=0,limit=5):
        counts=self.make_histogram(column,level);i=self.names.index(column)
        rows=self.connection.execute(f'SELECT key0,pn,gn FROM perkey WHERE pu>0 OR gu>0 ORDER BY key0 LIMIT {limit}').fetchall()
        examples=[]
        for k,pn,gn in rows:
            rawkeys={side:self.connection.execute(f'SELECT key_raw FROM {side}k WHERE key0=?',[k]).fetchone()[0] for side in ('p','g')}
            base={'key_normalized':dict(zip(self.keys,k)),'agent_key_raw_text':dict(zip(self.keys,rawkeys['p'])),
                  'gold_key_raw_text':dict(zip(self.keys,rawkeys['g'])),'agent_rows_with_key':pn,'gold_rows_with_key':gn}
            if pn==gn==1:
                p,g=[self.connection.execute(f'SELECT c{i} FROM {side}0 WHERE key0=?',[k]).fetchone()[0] for side in ('p','g')]
                base.update(kind='one_to_one',agent_value=p,gold_value=g)
            else:
                for side,label in [('p','agent_values'),('g','gold_values')]:
                    values=self.connection.execute(f'SELECT c{i},count(*) n FROM {side}0 WHERE key0=? GROUP BY c{i} ORDER BY c{i} NULLS FIRST LIMIT 5',[k]).fetchall()
                    base[label]=[{'value':value,'rows':n} for value,n in values]
                base.update(kind='duplicate_key_group_not_a_unique_row_pair',
                    sample_semantics='At most 5 distinct raw values per side in this key group; do not pair entries by list position.')
            examples.append(base)
        return counts,examples
