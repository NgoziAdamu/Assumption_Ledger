from annotate_dacomp_batch016 import *
def main():
 out={'basis':'015 complete raw inventory; diagnostics only, not verification evidence about a P','raw_comparisons':{},'trace_search':{}}
 for n in [10,15,16,19,20]:
  x=json.loads((REC/f'015_raw_impl-{n:03}.json').read_text()); chosen={10:'form_data',15:'item_data',16:'person_contact_email_address',19:'sales_subscription_summary',20:'conversation_part_history_data'}[n]
  out['raw_comparisons'][str(n)]={'source':f'records/015_raw_impl-{n:03}.json','table':chosen,'comparisons':[{k:v for k,v in r.items() if k not in ['gold','initial','agent']} for r in x['comparisons'] if r['raw_table']=='raw.'+chosen], 'sides':{s:{k:t[k] for k in ['row_count','columns','content_hash']} for s,v in x['sides'].items() for t in [v['tables'][chosen]]}}
 for n,ids in [(15,[44,45,46]),(16,[65,66,67,69,71,73,75,77,79,81,83])]:
  es=json.loads((REC/f'016_trace_impl-{n:03}.json').read_text());out['trace_search'][str(n)]={'event_ids':[x['id'] for x in es], 'selected_events':[e for e in es if e['id'] in ids], 'finding':('event45 changes raw import to pandas fetchdf/register; event44 gives duplicate-ATTACH reason' if n==15 else 'event66 still reports raw email 7284; subsequent events contain read-only queries or report writes, no located operation explaining retained 2448 rows')}
 x=json.loads((REC/'015_raw_impl-015.json').read_text());path=x['sides']['initial']['database'];q='SELECT count(*) n,count(parent_item_id) parent_nonnull FROM raw.item_data'
 with duckdb.connect(path,read_only=True) as c:
  r=c.execute(q);out['item_diagnostic']={'kind':'诊断查询','database':path,'sql':q,'columns':[d[0] for d in r.description],'rows':r.fetchall()}
  # Reproduce the trace's import path without writing the source.
  df=c.execute('SELECT parent_item_id FROM raw.item_data').fetchdf()
 with duckdb.connect(str(WORK/'item_import_diagnostic.duckdb')) as c:
  c.register('_raw_import',df);c.execute('CREATE OR REPLACE TABLE copied AS SELECT * FROM _raw_import');out['item_diagnostic']['private_import_result']=c.execute('DESCRIBE copied').fetchall();out['item_diagnostic']['private_sql']='source SELECT parent_item_id FROM raw.item_data -> fetchdf -> register(_raw_import) -> CREATE OR REPLACE TABLE copied AS SELECT * FROM _raw_import'
 save(REC/'016_raw_diagnostics.json',out);print('diagnostics saved',out['item_diagnostic'],flush=True)
if __name__=='__main__':main()
