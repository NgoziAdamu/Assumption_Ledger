from annotate_dacomp_batch014 import *
old=json.loads((REC/'014_input_before.json').read_text())['files'];after={str(p):fp(p) for p in map(Path,old)}
changes=[{'path':p,'before':old[p],'after':after[p]} for p in old if old[p]!=after[p]]
save(REC/'014_input_integrity.json',{'file_count':len(old),'database_count':sum(p.endswith('.duckdb') for p in old),'all_size_mtime_sha256_unchanged':not changes,'changes':changes,'files':after})
assert not changes,changes
print('All',len(old),'input fingerprints unchanged')
