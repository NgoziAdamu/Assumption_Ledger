from review_dacomp_batch022 import *
import re
for i in map(int,sys.argv[1:]):
 d=pkg(i);b=d['differences'];print('\nINDEX',i,b['table'],'date',b.get('candidate_date'),'rows',b['prediction_rows'],b['gold_rows']);print('DIFF',[(x['column'],x['l0_counts_verbatim']['mismatch_rows_or_minimum_pairs'],x['sample_key_groups'][:1]) for x in b['column_details'] if x['l0_counts_verbatim']['mismatch_rows_or_minimum_pairs']])
 for x in d['contract_specification']['blocks']:
  text=x['original_text']; start=text.find('      columns:');print('CONTRACT',text[:start] if start>=0 else text)
 print('AGENT',d['agent_final_SQL'][0]['text'])
 cols=[x['column'] for x in b['column_details'] if x['l0_counts_verbatim']['mismatch_rows_or_minimum_pairs']]
 for x in d['gold_SQL_仅供定位差异']:
  lines=x['text'].splitlines();ids={j for j,l in enumerate(lines) if any(re.search(r'\b'+re.escape(col)+r'\b',l,re.I) for col in cols) or re.search('WHERE|JOIN|GROUP BY|QUALIFY',l,re.I)}
  ids={j for i in ids for j in range(max(0,i-2),min(len(lines),i+3))};print('GOLD EXCERPTS','\n'.join(f'{j+1}: {lines[j]}' for j in sorted(ids)))
