"""Read-only document/header extraction and files_read joins; no agent execution."""
from pathlib import Path
from collections import Counter, defaultdict
import csv
import hashlib
import importlib.metadata
import json
import os
import posixpath
import re
import sqlite3
import sys
import xml.etree.ElementTree as ET
import zipfile

sys.dont_write_bytecode=True
import numpy as np
import cdflib
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/kramabench/data'
OLD=Path('/home/katherine/dac/benchmarks/KramaBench')
OUT=ROOT/'records/031_kramabench_docs'
DOMAINS=['archeology','astronomy','biomedical','environment','legal','wildfire']
DOC_NAME=re.compile(r'readme|descrip|dictionary|codebook|metadata|notes|variable',re.I)
DOC_SHEET=re.compile(r'read\s*me|notes?|description|info|instruction|metadata|dictionary|codebook|guide|contents|legend|overview|about|说明|注释',re.I)
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def sha(data):return hashlib.sha256(data).hexdigest()
def dump(path,obj):
    with path.open('x',encoding='utf-8') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
def write_csv(path,rows):
    with path.open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def plain(value):
    if isinstance(value,np.ndarray):return value.tolist()
    if isinstance(value,np.generic):return value.item()
    if isinstance(value,dict):return {k:plain(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [plain(v) for v in value]
    return value
def decode(data):
    if data.startswith(b'\xff\xfe'):return data.decode('utf-16-le'),'utf-16-le (BOM retained)'
    if data.startswith(b'\xfe\xff'):return data.decode('utf-16-be'),'utf-16-be (BOM retained)'
    try:return data.decode('utf-8'),'utf-8'
    except UnicodeDecodeError:
        try:return data.decode('cp1252'),'cp1252 fallback (not independently confirmed)'
        except UnicodeDecodeError:return data.decode('latin-1'),'latin-1 fallback (not independently confirmed)'
def fence(key,text,lang='text'):
    marks='`'*max(3,1+max([len(x.group()) for x in re.finditer(r'`+',text)] or [0]))
    sep='' if text.endswith('\n') else '\n'
    return f'<!-- excerpt:{key} chars:{len(text)} -->\n{marks}{lang}\n{text}{sep}{marks}\n<!-- /excerpt:{key} -->\n\n'

def shared_text(node):
    parts=[]
    for child in node:
        if child.tag==f'{{{NS["s"]}}}t':parts.append(child.text or '')
        elif child.tag==f'{{{NS["s"]}}}r':
            parts.extend(t.text or '' for t in child.findall('s:t',NS))
    return ''.join(parts)

def workbook(path):
    """Use original OOXML values, not pandas inference or formatted rendering."""
    result=[]
    with zipfile.ZipFile(path) as z:
        shared=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            with z.open('xl/sharedStrings.xml') as f:
                for _,el in ET.iterparse(f,events=['end']):
                    if el.tag==f'{{{NS["s"]}}}si':shared.append(shared_text(el));el.clear()
        rels={r.attrib['Id']:r.attrib['Target'] for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        wb=ET.fromstring(z.read('xl/workbook.xml'))
        for sheet in wb.find('s:sheets',NS):
            name=sheet.attrib['name'];is_doc=bool(DOC_SHEET.search(name))
            rid=sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
            target=rels[rid]
            member=target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join('xl',target))
            rows={};dimension=None
            with z.open(member) as f:
                for _,el in ET.iterparse(f,events=['end']):
                    if el.tag==f'{{{NS["s"]}}}dimension':dimension=el.attrib.get('ref')
                    if el.tag!=f'{{{NS["s"]}}}row':continue
                    rn=int(el.attrib['r'])
                    if not is_doc and rn>10:break
                    cells=[]
                    for cell in el.findall('s:c',NS):
                        typ=cell.attrib.get('t','n');val=cell.find('s:v',NS);formula=cell.find('s:f',NS)
                        item={'cell':cell.attrib['r'],'type':typ}
                        if typ=='s':
                            item['text']=shared[int(val.text)] if val is not None and val.text is not None else None
                        elif typ=='inlineStr':
                            inline=cell.find('s:is',NS);item['text']=shared_text(inline) if inline is not None else ''
                        else:item['raw_value']=val.text if val is not None else None
                        if formula is not None:
                            item['formula']=formula.text;item['formula_attributes']=dict(formula.attrib)
                        if 's' in cell.attrib:item['style_index']=cell.attrib['s']
                        cells.append(item)
                    rows[rn]={'row':rn,'cells':cells};el.clear()
            limit=max(rows,default=0) if is_doc else 10
            result.append({'name':name,'state':sheet.attrib.get('state','visible'),'xml_member':member,'dimension':dimension,
                           'document_sheet':is_doc,'scope':'all_rows' if is_doc else 'first_10_physical_rows',
                           'rows':[rows.get(n,{'row':n,'cells':[]}) for n in range(1,limit+1)]})
    return result

def package_files_read(path):
    text=path.read_bytes().decode('utf-8');found=defaultdict(list)
    for m in re.finditer(r'^<!-- original:(step\.(\d+)\.files_read) chars:(\d+) -->\n`{3,}json\n',text,re.M):
        value=text[m.end():m.end()+int(m.group(3))]
        for filename in json.loads(value):found[filename].append(int(m.group(2)))
    return dict(found)

def main():
    assert not OUT.exists()
    OUT.mkdir()
    inventory=[];excerpts=[];units=[];sheets=[];source_hashes={};doc_texts={};per_domain={}
    for domain in DOMAINS:
        parts=[f'# KramaBench {domain}：说明材料及文件开头摘录\n\n',
               '以下为原文/原字段摘录；不解释其含义。文本保持解码后的字符与换行；Excel 以原 OOXML 单元格坐标和值呈现，不重排、不推断表头、不计算公式。\n\n']
        files=sorted(p for p in (DATA/domain/'input').rglob('*') if p.is_file())
        for p in files:
            assert not p.is_symlink()
            data=p.read_bytes();source_hashes[str(p)]=sha(data)
            rel=p.relative_to(DATA).as_posix();inside=p.relative_to(DATA/domain/'input').as_posix();ext=p.suffix
            key=f'{domain}.{len(inventory)+1}'
            row={'领域':domain,'相对路径':rel,'领域input内相对路径':inside,'大小_字节':len(data),'扩展名':ext,'SHA256':sha(data)}
            inventory.append(row)
            units.append({'domain':domain,'path':rel,'kind':'file_excerpt_or_metadata','parent_path':rel,'input_relative':inside})
            parts.append(f'## 文件：`{rel}`\n\n来源：`{p.relative_to(ROOT)}`；{len(data):,} 字节；扩展名 `{ext}`。\n\n')
            def emit(text,kind,extra=None,language='text'):
                eid=key+'.'+str(sum(e['source']==str(p) for e in excerpts)+1)
                excerpts.append({'id':eid,'domain':domain,'source':str(p),'kind':kind,'chars':len(text),'text_sha256':sha(text.encode()),**(extra or {})})
                parts.append(f'摘录范围：{kind}。\n\n'+fence(eid,text,language))
            lower=ext.lower()
            if lower=='.xlsx':
                book=workbook(p);emit(json.dumps([{'name':x['name'],'state':x['state']} for x in book],ensure_ascii=False,indent=2),'all_sheet_names',language='json')
                for sheet in book:
                    sheets.append({'domain':domain,'path':rel,**sheet})
                    parts.append('### 页：`'+sheet['name']+'`\n\n')
                    payload='\n'.join(json.dumps(r,ensure_ascii=False) for r in sheet['rows'])+'\n'
                    emit(payload,'excel_'+sheet['scope'],{'sheet':sheet['name'],'xml_member':sheet['xml_member'],'document_sheet':sheet['document_sheet']},'jsonl')
                    if sheet['document_sheet']:
                        units.append({'domain':domain,'path':rel+'#sheet='+sheet['name'],'kind':'excel_document_sheet','parent_path':rel,'input_relative':inside,'sheet':sheet['name']})
            elif lower=='.npz':
                arrays=[]
                with zipfile.ZipFile(p) as z:
                    for name in z.namelist():
                        if not name.endswith('.npy'):continue
                        with z.open(name) as f:
                            version=np.lib.format.read_magic(f)
                            assert version in [(1,0),(2,0)],version
                            reader=np.lib.format.read_array_header_1_0 if version==(1,0) else np.lib.format.read_array_header_2_0
                            shape,fortran,dtype=reader(f)
                            arrays.append({'key':name[:-4],'shape':list(shape),'dtype':str(dtype),'fortran_order':fortran})
                emit(json.dumps(arrays,ensure_ascii=False,indent=2),'npz_keys_shapes_header_only',language='json')
            elif lower=='.cdf':
                c=cdflib.CDF(p);info=c.cdf_info();variables=[]
                for name in info.rVariables+info.zVariables:
                    attrs=plain(c.varattsget(name))
                    variables.append({'name':name,'attributes':attrs,'DESCRIPTION_present':'DESCRIPTION' in attrs,'UNITS_present':'UNITS' in attrs})
                emit(json.dumps(variables,ensure_ascii=False,indent=2),'cdf_variable_names_and_attributes_no_variable_data',language='json')
            elif lower=='.gpkg':
                conn=sqlite3.connect(p.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
                layers=[]
                for name,typ in conn.execute('SELECT table_name,data_type FROM gpkg_contents ORDER BY table_name'):
                    fields=conn.execute('PRAGMA table_info("'+name.replace('"','""')+'")').fetchall()
                    layers.append({'layer_name':name,'data_type':typ,'fields':[{'name':x[1],'type':x[2]} for x in fields]})
                conn.close();emit(json.dumps(layers,ensure_ascii=False,indent=2),'gpkg_layer_names_and_field_names_readonly',language='json')
            else:
                text,encoding=decode(data);lines=text.splitlines(keepends=True)
                if lower=='.sp3':selected=''.join(lines[:30]);kind='first_30_lines'
                elif lower=='.lst':selected=''.join(lines[:5]);kind='lst_first_5_lines_no_header_interpretation'
                elif lower in ['.csv','.tsv'] and not DOC_NAME.search(p.name):selected=''.join(lines[:5]);kind='first_5_physical_lines'
                else:
                    selected=text if len(text)<=50000 else ''.join(lines[:200]);kind='full_text' if len(text)<=50000 else 'first_200_lines'
                emit(selected,kind,{'encoding':encoding,'source_chars':len(text),'source_lines':len(lines),'excerpt_lines':len(selected.splitlines()),'filename_doc_keyword':bool(DOC_NAME.search(p.name))})
            # The original repository data path is a byte-identical source twin.
            twin=OLD/'data'/domain/'input'/inside
            assert twin.is_file() and sha(twin.read_bytes())==sha(data)
        per_domain[domain]={'files':len(files),'bytes':sum(x['大小_字节'] for x in inventory if x['领域']==domain)}
        doc_texts[domain]=parts
        print('Extracted',domain,len(files),'files',flush=True)

    # Search the local repository for document containers, without executing any.
    repo_candidates=[]
    for directory,dirs,files in os.walk(OLD,followlinks=False):
        dirs[:]=[d for d in dirs if d!='.git' and d!='__pycache__']
        for name in files:
            p=Path(directory)/name;rel=p.relative_to(OLD).as_posix()
            if p.suffix.lower() in ['.md','.rst','.pdf','.ipynb'] or DOC_NAME.search(name):
                if p.is_symlink():continue
                data=p.read_bytes();candidate={'path':str(p),'relative_path':rel,'bytes':len(data),'sha256':sha(data),'included_domains':[]}
                if rel=='README.md':candidate.update(included_domains=DOMAINS,scope='full_text')
                elif rel=='quickstart/2023_Annual_Beach_Report.pdf':candidate.update(included_domains=['environment'],scope='all_pdf_pages_text_layer')
                elif rel=='quickstart/quickstart_questions.ipynb':candidate.update(included_domains=['environment'],scope='all_markdown_cells')
                elif rel.startswith('data/'):
                    candidate['scope']='already_extracted_from_byte_identical_local_input'
                else:candidate['scope']='not_data_document_or_no_dataset_description; inspected_markdown_catalog'
                if p.suffix.lower()=='.ipynb':
                    nb=json.loads(data);cells=[(i,''.join(c.get('source',[]))) for i,c in enumerate(nb['cells']) if c['cell_type']=='markdown']
                    candidate['markdown_cells']=[{'index':i,'chars':len(text),'text':text} for i,text in cells]
                elif p.suffix.lower() in ['.md','.rst']:
                    candidate['text']=decode(data)[0]
                repo_candidates.append(candidate)
                if not candidate['included_domains']:continue
                source_hashes[str(p)]=sha(data)
                chunks=[]
                if candidate['scope']=='full_text':chunks=[('full_text',decode(data)[0],{})]
                elif candidate['scope']=='all_markdown_cells':
                    chunks=[('notebook_markdown_cell',text,{'cell_index':i}) for i,text in cells]
                else:
                    pdf=PdfReader(p)
                    chunks=[('pdf_page_text_layer',page.extract_text() or '',{'page':i+1}) for i,page in enumerate(pdf.pages)]
                    candidate['pdf_pages']=len(chunks);candidate['empty_text_pages']=[x[2]['page'] for x in chunks if not x[1]]
                for domain in candidate['included_domains']:
                    doc_texts[domain].append(f'## 本地仓库说明文档：`{p}`\n\n摘录范围：{candidate["scope"]}；仓库内路径 `{rel}`。\n\n')
                    units.append({'domain':domain,'path':str(p),'kind':'repository_document','parent_path':str(p),'input_relative':None})
                    for i,(kind,text,extra) in enumerate(chunks,1):
                        eid=f'{domain}.repo.{len(excerpts)+1}'
                        excerpts.append({'id':eid,'domain':domain,'source':str(p),'kind':kind,'chars':len(text),'text_sha256':sha(text.encode()),**extra})
                        doc_texts[domain].append(f'原文片段 {i}，定位：{json.dumps(extra,ensure_ascii=False)}。\n\n'+fence(eid,text))

    for domain,parts in doc_texts.items():
        with (OUT/(domain+'.md')).open('x',encoding='utf-8',newline='') as f:f.write(''.join(parts))
    final_rows=list(csv.DictReader((ROOT/'records/029_kramabench_final_scores.csv').open()))
    failed=[r for r in final_rows if r['最终状态'] in ['未通过','未交卷']];assert len(failed)==42
    old_index=json.loads((ROOT/'records/028_kramabench_package_index.json').read_bytes())
    read_rows=[];package_records={}
    for r in failed:
        tid=r['题号'];domain=tid.split('-')[0];package=ROOT/'records/028_kramabench_packages'/(tid+'.md')
        source_hashes[str(package)]=sha(package.read_bytes());observed=package_files_read(package)
        assert sorted(observed)==old_index[tid]['unique_files_read']
        package_records[tid]=observed
        for unit in [u for u in units if u['domain']==domain]:
            inside=unit['input_relative']
            if inside is None:aliases={unit['parent_path']}
            else:
                aliases={'data/'+inside,str(OLD/'data'/domain/'input'/inside),str(DATA/domain/'input'/inside),
                         'data/kramabench/data/'+domain+'/input/'+inside}
            matches=sorted(x for x in observed if x in aliases)
            status=('是（files_read 命中文件）' if matches else '未记录') if unit['kind']!='excel_document_sheet' else '无法判定（files_read 无页名）'
            read_rows.append({'题号':tid,'领域':domain,'说明文件路径':unit['path'],'材料单元':unit['kind'],
                              'agent是否读过':status,'文件级files_read是否命中':'是' if matches else '否',
                              '命中的files_read原值':json.dumps(matches,ensure_ascii=False),
                              '命中的材料包步骤':json.dumps({x:observed[x] for x in matches},ensure_ascii=False),
                              '材料包来源':str(package.relative_to(ROOT))})
    for name,h in source_hashes.items():assert sha(Path(name).read_bytes())==h,name
    directory_summary=[]
    groups=defaultdict(lambda:[0,0])
    for row in inventory:
        p=Path(row['领域input内相对路径']);bucket=p.parts[0] if len(p.parts)>1 else '.'
        g=groups[(row['领域'],bucket)];g[0]+=1;g[1]+=row['大小_字节']
    for (domain,bucket),(count,size) in sorted(groups.items()):directory_summary.append({'domain':domain,'input_directory':bucket,'files':count,'bytes':size})
    summary={'domains':per_domain,'files':len(inventory),'bytes':sum(x['大小_字节'] for x in inventory),
             'excel_files':sum(x['扩展名'].lower()=='.xlsx' for x in inventory),'excel_sheets':len(sheets),
             'excel_document_sheets':[{k:x[k] for k in ['domain','path','name','scope']} for x in sheets if x['document_sheet']],
             'excerpt_blocks':len(excerpts),'extracted_payload_chars':sum(x['chars'] for x in excerpts),
             'domain_markdown_chars':{d:len(''.join(parts)) for d,parts in doc_texts.items()},
             'text_encoding_counts':dict(Counter(x['encoding'] for x in excerpts if 'encoding' in x)),
             'read_matrix_rows':len(read_rows),'read_status_counts':dict(Counter(x['agent是否读过'] for x in read_rows)),
             'failed_tasks':42,'all_source_hashes_unchanged':True,'all_input_files_match_original_repository':True,
             'dependencies':{d.metadata['Name']:d.version for d in importlib.metadata.distributions()},
             'document_sheet_name_regex':DOC_SHEET.pattern,'filename_document_regex':DOC_NAME.pattern,
             'directory_summary':directory_summary}
    write_csv(ROOT/'records/031_kramabench_docs_files.csv',inventory)
    write_csv(ROOT/'records/031_kramabench_docs_read.csv',read_rows)
    dump(ROOT/'records/031_kramabench_docs_excerpts.json',excerpts)
    dump(ROOT/'records/031_kramabench_docs_units.json',units)
    dump(ROOT/'records/031_kramabench_docs_sheets.json',sheets)
    dump(ROOT/'records/031_kramabench_docs_repository_search.json',repo_candidates)
    dump(ROOT/'records/031_kramabench_docs_files_read_evidence.json',package_records)
    dump(ROOT/'records/031_kramabench_docs_source_hashes.json',source_hashes)
    dump(ROOT/'records/031_kramabench_docs_summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ['dependencies','directory_summary']},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
