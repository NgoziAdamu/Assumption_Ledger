"""Verify extracts against files and join rows against package files_read only."""
from pathlib import Path
from collections import Counter,defaultdict
import csv
import hashlib
import importlib.util
import json
import re
import sqlite3
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'records'
spec=importlib.util.spec_from_file_location('extract',R/'031_extract_kramabench_docs.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
import numpy as np
import cdflib
from pypdf import PdfReader

def main():
    manifest=json.loads((R/'031_kramabench_docs_excerpts.json').read_bytes())
    sheets=json.loads((R/'031_kramabench_docs_sheets.json').read_bytes())
    units=json.loads((R/'031_kramabench_docs_units.json').read_bytes())
    summary=json.loads((R/'031_kramabench_docs_summary.json').read_bytes())
    hashes=json.loads((R/'031_kramabench_docs_source_hashes.json').read_bytes())
    inventory=list(csv.DictReader((R/'031_kramabench_docs_files.csv').open()))
    read_rows=list(csv.DictReader((R/'031_kramabench_docs_read.csv').open()))
    expected_paths={p.relative_to(mod.DATA).as_posix() for p in mod.DATA.rglob('*') if p.is_file()}
    assert len(inventory)==1742 and {x['相对路径'] for x in inventory}==expected_paths
    for row in inventory:
        p=mod.DATA/row['相对路径'];data=p.read_bytes()
        assert len(data)==int(row['大小_字节']) and hashlib.sha256(data).hexdigest()==row['SHA256']
        assert row['扩展名']==p.suffix
        twin=mod.OLD/'data'/row['相对路径']
        assert twin.read_bytes()==data
    blocks={};counts=Counter();source_cache={};pdf_cache={};nb_cache={}
    for domain in mod.DOMAINS:
        text=(R/'031_kramabench_docs'/(domain+'.md')).read_bytes().decode('utf-8')
        assert len(text)==summary['domain_markdown_chars'][domain]
        pattern=re.compile(r'^<!-- excerpt:([\w.]+) chars:(\d+) -->\n(`{3,})(?:text|json|jsonl)\n',re.M)
        pos=0
        while m:=pattern.search(text,pos):
            key,n,f=m.groups();end=m.end()+int(n);payload=text[m.end():end]
            suffix=('' if payload.endswith('\n') else '\n')+f+'\n<!-- /excerpt:'+key+' -->\n'
            assert text[end:end+len(suffix)]==suffix
            assert key not in blocks;blocks[key]=payload;pos=end+len(suffix)
    assert set(blocks)=={x['id'] for x in manifest}
    for rec in manifest:
        payload=blocks[rec['id']];p=Path(rec['source']);kind=rec['kind']
        assert len(payload)==rec['chars'] and hashlib.sha256(payload.encode()).hexdigest()==rec['text_sha256']
        if 'encoding' in rec or kind=='full_text':
            if str(p) not in source_cache:source_cache[str(p)]=mod.decode(p.read_bytes())
            full,encoding=source_cache[str(p)]
            if 'encoding' in rec:assert encoding==rec['encoding']
            limits={'first_5_physical_lines':5,'first_30_lines':30,'lst_first_5_lines_no_header_interpretation':5,'first_200_lines':200}
            expected=full if kind=='full_text' else ''.join(full.splitlines(keepends=True)[:limits[kind]])
            assert payload==expected
            assert p.read_bytes().startswith(payload.encode(encoding.split(' ')[0]))
            counts['verbatim_text_blocks']+=1
        elif kind=='all_sheet_names':
            with zipfile.ZipFile(p) as z:
                wb=ET.fromstring(z.read('xl/workbook.xml'))
                expected=[{'name':s.attrib['name'],'state':s.attrib.get('state','visible')} for s in wb.find('s:sheets',mod.NS)]
            assert json.loads(payload)==expected;counts['workbook_sheet_lists']+=1
        elif kind.startswith('excel_'):
            sheet=next(s for s in sheets if s['path']==p.relative_to(mod.DATA).as_posix() and s['name']==rec['sheet'])
            assert [json.loads(x) for x in payload.splitlines()]==sheet['rows']
            # Independent XML coverage and lexical numeric/formula checks.
            with zipfile.ZipFile(p) as z:
                shared=[]
                if 'xl/sharedStrings.xml' in z.namelist():
                    for el in ET.fromstring(z.read('xl/sharedStrings.xml')):
                        shared.append(mod.shared_text(el))
                all_rows={}
                with z.open(rec['xml_member']) as sheet_file:
                    for _,element in ET.iterparse(sheet_file,events=['end']):
                        if element.tag!=f'{{{mod.NS["s"]}}}row':continue
                        number=int(element.attrib['r'])
                        if not rec['document_sheet'] and number>10:break
                        all_rows[number]=element
                wanted=max(all_rows,default=0) if rec['document_sheet'] else 10
                assert len(sheet['rows'])==wanted
                for row in sheet['rows']:
                    source_row=all_rows.get(row['row']);cells=[] if source_row is None else source_row.findall('s:c',mod.NS)
                    assert [c.attrib['r'] for c in cells]==[c['cell'] for c in row['cells']]
                    for original,saved in zip(cells,row['cells']):
                        typ=original.attrib.get('t','n');value=original.find('s:v',mod.NS)
                        assert typ==saved['type']
                        if typ=='s':expected=shared[int(value.text)] if value is not None and value.text is not None else None;assert saved['text']==expected
                        elif typ=='inlineStr':
                            node=original.find('s:is',mod.NS);assert saved['text']==(mod.shared_text(node) if node is not None else '')
                        else:assert saved['raw_value']==(value.text if value is not None else None)
                        formula=original.find('s:f',mod.NS)
                        if formula is not None:assert saved['formula']==formula.text
                        counts['excel_cells']+=1
            counts['excel_sheets']+=1
        elif kind=='npz_keys_shapes_header_only':
            data=json.loads(payload)
            with np.load(p,allow_pickle=False) as arrays:
                assert [x['key'] for x in data]==arrays.files
                for x in data:assert x['shape']==list(arrays[x['key']].shape)
            counts['npz']+=1
        elif kind=='cdf_variable_names_and_attributes_no_variable_data':
            c=cdflib.CDF(p);info=c.cdf_info();data=json.loads(payload)
            assert [x['name'] for x in data]==info.rVariables+info.zVariables
            for x in data:assert x['attributes']==mod.plain(c.varattsget(x['name']))
            counts['cdf_variables']+=len(data)
        elif kind=='gpkg_layer_names_and_field_names_readonly':
            conn=sqlite3.connect(p.resolve().as_uri()+'?mode=ro&immutable=1',uri=True);data=json.loads(payload)
            assert [x['layer_name'] for x in data]==[r[0] for r in conn.execute('SELECT table_name FROM gpkg_contents ORDER BY table_name')]
            for x in data:
                columns=conn.execute('PRAGMA table_info("'+x['layer_name'].replace('"','""')+'")').fetchall()
                assert x['fields']==[{'name':y[1],'type':y[2]} for y in columns]
            conn.close();counts['gpkg_layers']+=len(data)
        elif kind=='pdf_page_text_layer':
            if str(p) not in pdf_cache:pdf_cache[str(p)]=[x.extract_text() or '' for x in PdfReader(p).pages]
            assert payload==pdf_cache[str(p)][rec['page']-1];counts['pdf_pages']+=1
        elif kind=='notebook_markdown_cell':
            if str(p) not in nb_cache:nb_cache[str(p)]=json.loads(p.read_bytes())
            cell=nb_cache[str(p)]['cells'][rec['cell_index']]
            assert cell['cell_type']=='markdown' and payload==''.join(cell['source']);counts['notebook_markdown_cells']+=1
        else:raise AssertionError(kind)
    selected={r['题号'] for r in csv.DictReader((R/'029_kramabench_final_scores.csv').open()) if r['最终状态'] in ['未通过','未交卷']}
    assert len(selected)==42 and {x['题号'] for x in read_rows}==selected
    evidence=json.loads((R/'031_kramabench_docs_files_read_evidence.json').read_bytes())
    actual=set()
    for row in read_rows:
        tid=row['题号'];domain=tid.split('-')[0];key=(tid,row['说明文件路径']);assert key not in actual;actual.add(key)
        unit=next(u for u in units if u['domain']==domain and u['path']==row['说明文件路径'])
        package=ROOT/row['材料包来源'];observed=mod.package_files_read(package)
        assert observed==evidence[tid]
        inside=unit['input_relative']
        aliases={unit['parent_path']} if inside is None else {'data/'+inside,str(mod.OLD/'data'/domain/'input'/inside),str(mod.DATA/domain/'input'/inside),'data/kramabench/data/'+domain+'/input/'+inside}
        expected=sorted(p for p in observed if p in aliases)
        assert json.loads(row['命中的files_read原值'])==expected
        assert json.loads(row['命中的材料包步骤'])=={p:observed[p] for p in expected}
        assert row['文件级files_read是否命中']==('是' if expected else '否')
        if unit['kind']=='excel_document_sheet':assert row['agent是否读过']=='无法判定（files_read 无页名）'
        else:assert row['agent是否读过']==('是（files_read 命中文件）' if expected else '未记录')
    assert actual=={(tid,u['path']) for tid in selected for u in units if u['domain']==tid.split('-')[0]}
    for name,digest in hashes.items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest
    result={'passed':True,'inventory_files':len(inventory),'excerpt_blocks':len(blocks),**counts,
            'read_matrix_rows':len(read_rows),'all_read_matrix_rows_checked':True,'files_read_source':'actual 028 Markdown per-step files_read blocks',
            'excel_sheet_reads_not_inferred':True,'source_hashes_verified':len(hashes),'sources_unchanged':True,
            'original_repository_data_twins_verified':1742,'agent_or_model_calls':0}
    with (R/'031_kramabench_docs_validation.json').open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
