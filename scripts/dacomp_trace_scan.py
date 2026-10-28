"""Static SQL/contract scans and read-only output profiles for task 008."""

from collections import defaultdict
from itertools import combinations
from pathlib import Path
import hashlib
import re

import sqlglot
from sqlglot import exp
from sqlglot.optimizer.scope import Scope, build_scope
import yaml
from yaml.nodes import MappingNode, SequenceNode

from compare_dacomp_staging import plain, quote


BLOCKED_CONSTANT_PATTERN = re.compile(r'AC[0-9a-fA-F]{32}')


def protect_constant_values(output):
    """Do not serialize the identifier format blocked by repository push protection."""
    for column in output.get('constant_nonnull_columns') or []:
        value=column.get('value')
        if isinstance(value,str) and BLOCKED_CONSTANT_PATTERN.fullmatch(value):
            column.update(value=None,value_sha256=hashlib.sha256(value.encode()).hexdigest(),
                value_length=len(value),value_omitted_reason='github_push_protection_Twilio_Account_SID_format',
                value_source='original retained database, this table and column; read only')
    return output


def layer_key(layer):
    return 'marts' if layer.lower() in ('mart', 'marts') else layer.lower()


def table_key(schema, name):
    return layer_key(schema), name.lower()


def location(node, text):
    marks = [n.meta for n in node.walk() if 'start' in n.meta]
    if not marks:
        return {'line': None, 'end_line': None}
    start = min(m['start'] for m in marks)
    end = max(m.get('end', m['start']) for m in marks)
    return {'line': text.count('\n', 0, start) + 1, 'end_line': text.count('\n', 0, end) + 1}


def contract_index(path):
    """Preserve every original table/column block, including duplicate definitions."""
    path = Path(path)
    text = path.read_text()
    try:
        root = yaml.compose(text)
        mode = 'strict'
    except yaml.YAMLError:
        root = yaml.compose(text.replace('\\', '\\\\'))
        mode = 'escape_backslashes_in_memory_for_structure_only'
    lines = text.splitlines(keepends=True)
    result = defaultdict(list)

    def block(node):
        start = node.start_mark.line
        end = node.end_mark.line
        if end < len(lines) and lines[end][:node.end_mark.column].strip():
            end += 1
        # YAML end marks may point at the next sequence item's indentation.
        while end > start and (not lines[end - 1].strip() or lines[end - 1].lstrip().startswith('#')):
            end -= 1
        return {'path': str(path), 'start_line': start + 1, 'end_line': end,
                'original_text': ''.join(lines[start:end])}

    def walk(node, trail):
        if isinstance(node, MappingNode):
            mapping = {k.value: v for k, v in node.value}
            if 'columns' in mapping and ('name' in mapping or len(trail) >= 3):
                name = plain(mapping['name']) if 'name' in mapping else trail[-1]
                if trail[:2] == ['staging_contract', 'tables']:
                    layer = 'staging'
                elif trail and trail[0] == 'modeling_spec':
                    layer = str(trail[1]).removesuffix('_models')
                else:
                    layer = None
                if layer and isinstance(name, str):
                    value = plain(node)
                    columns = {}
                    cn = mapping['columns']
                    entries = list(enumerate(cn.value)) if isinstance(cn, SequenceNode) else [(k.value,v) for k,v in cn.value]
                    for index, column_node in entries:
                        item = plain(column_node)
                        cname = item.get('name', index)
                        columns[str(cname).lower()] = {**block(column_node), 'name': cname,
                            'description': item.get('description'), 'specification': item}
                    result[table_key(layer, name)].append({**block(node), 'yaml_path': trail,
                        'specification': value, 'columns': columns})
                    return
            for key, value in node.value:
                walk(value, trail + [key.value])
        elif isinstance(node, SequenceNode):
            for index, value in enumerate(node.value):
                walk(value, trail + [index])
    walk(root, [])
    return dict(result), mode


def column_contract(blocks, name):
    descriptions = [b['columns'][name.lower()] for b in blocks if name.lower() in b['columns']]
    return {'status': 'found' if descriptions else '契约未描述', 'definitions': descriptions,
            'meaning_description_status': 'explicit_description' if any(c['description'] for c in descriptions) else '契约未描述含义'}


SOURCE_PATTERN = re.compile(r'(?<![\w.])(?:raw|staging|intermediate|marts?|marketing|sales|service|utils)\.[A-Za-z_][A-Za-z_0-9]*(?![\w.])', re.I)


def canonical_source(text):
    # Only normalize identifier spelling and the actual mart/marts schema alias.
    parts = text.replace('"', '').replace('`', '').lower().split('.')
    if len(parts) >= 2:
        parts[-2] = layer_key(parts[-2])
    return '.'.join(parts)


def contract_sources(blocks):
    references = []
    for block in blocks:
        spec = block['specification']
        for field in ('source_table', 'source_models', 'source_tables', 'sources', 'depends_on', 'upstream_tables', 'inputs'):
            value = spec.get(field)
            if value is not None:
                for item in value if isinstance(value, list) else [value]:
                    if isinstance(item, str):
                        references.append({'name': item, 'canonical': canonical_source(item),
                                           'basis': field, 'path': block['path'], 'block_start_line': block['start_line']})
        for offset, line in enumerate(block['original_text'].splitlines()):
            for match in SOURCE_PATTERN.finditer(line):
                references.append({'name': match.group(), 'canonical': canonical_source(match.group()),
                    'basis': 'explicit_schema_qualified_reference_in_original_block',
                    'path': block['path'], 'line': block['start_line'] + offset, 'line_text': line})
    return {'status': 'specified' if references else '契约未指定', 'references': references,
            'canonical_names': sorted({r['canonical'] for r in references})}


RUNTIME_PATTERN = re.compile(
    r'\b(?:CURRENT_DATE|CURRENT_TIMESTAMP|CURRENT_TIME|LOCALTIME|LOCALTIMESTAMP|SYSDATE|SYSTIMESTAMP)\b'
    r'|\b(?:NOW|GETDATE|GETUTCDATE|SYSDATETIME|SYSUTCDATETIME|UTC_DATE|UTC_TIMESTAMP|'
    r'CLOCK_TIMESTAMP|STATEMENT_TIMESTAMP|TRANSACTION_TIMESTAMP)\s*\('
    r'|\bTODAY\b|\bcurrent\s+(?:date|timestamp|time)\b', re.I)


def lexical_regions(text):
    """Classify token occurrences without treating comments/strings as SQL calls."""
    region = ['code'] * len(text)
    for match in re.finditer(r"--[^\n]*|/\*[\s\S]*?\*/|'(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"", text):
        kind = 'comment' if match.group().startswith(('--', '/*')) else 'string' if match.group().startswith("'") else 'quoted_identifier'
        region[match.start():match.end()] = [kind] * (match.end() - match.start())
    return region


def runtime_hits(text, path, start_line=1, sql=False):
    regions = lexical_regions(text) if sql else None
    lines = text.splitlines()
    hits = []
    for match in RUNTIME_PATTERN.finditer(text):
        relative_line = text.count('\n', 0, match.start())
        hits.append({'path': str(path), 'line': start_line + relative_line,
            'column': match.start() - text.rfind('\n', 0, match.start()), 'matched_text': match.group(),
            'line_text': lines[relative_line], 'context': regions[match.start()] if regions else 'contract_text'})
    # DuckDB/SQL engines also accept explicit relative-time string tokens.
    if sql:
        for match in re.finditer(r"'(?P<token>now|today|yesterday|tomorrow)'", text, re.I):
            hits.append({'path': str(path), 'line': start_line + text.count('\n', 0, match.start()),
                'column': match.start() - text.rfind('\n', 0, match.start()), 'matched_text': match.group(),
                'line_text': lines[text.count('\n', 0, match.start())], 'context': 'relative_time_string_lexeme_uninterpreted'})
    return sorted(hits, key=lambda h:(h['line'], h['column']))


def literal_kind(expression):
    node = expression.unalias()
    casts = []
    while isinstance(node, (exp.Cast, exp.TryCast, exp.Paren)):
        if isinstance(node, (exp.Cast, exp.TryCast)):
            casts.append(node.args['to'].sql(dialect='duckdb'))
        node = node.this
    if isinstance(node, exp.Null):
        return {'kind': 'null_literal', 'casts': casts, 'literal_sql': 'NULL'}
    if isinstance(node, (exp.Literal, exp.Boolean)) or isinstance(node, exp.Neg) and isinstance(node.this, exp.Literal):
        return {'kind': 'nonnull_literal', 'casts': casts, 'literal_sql': node.sql(dialect='duckdb')}
    return None


def sql_scan(path, database_columns=None):
    path = Path(path)
    text = path.read_text()
    try:
        roots = [r for r in sqlglot.parse(text, read='duckdb') if r]
        if len(roots) != 1:
            raise ValueError('Expected one final query per file')
        scope = build_scope(roots[0])
        if scope is None:
            raise ValueError('No SELECT scope')
    except Exception as error:
        return {'path': str(path), 'status': 'parse_failed', 'error': str(error), 'runtime_hits': runtime_hits(text,path,sql=True),
                'sources': None, 'outputs': None, 'parser': sqlglot.__version__}
    visited, sources, unresolved, generators = set(), {}, [], []

    def collect(current):
        if id(current) in visited:
            return
        visited.add(id(current))
        for _, (_, source) in current.selected_sources.items():
            if isinstance(source, Scope):
                collect(source)
            elif isinstance(source, exp.Table) and isinstance(source.this, exp.Identifier):
                name = '.'.join(part.name for part in source.parts)
                canonical = canonical_source(name)
                entry = sources.setdefault(canonical, {'name': name, 'canonical': canonical, 'locations': []})
                entry['locations'].append(location(source, text))
            elif isinstance(source, exp.Table) and isinstance(source.this,(exp.GenerateSeries,exp.Unnest)):
                generators.append({'expression':source.sql(dialect='duckdb'),'kind':'row_generator_not_a_stored_source_table',**location(source,text)})
            else:
                unresolved.append(source.sql(dialect='duckdb'))
        for sub in current.subquery_scopes + current.set_operation_scopes + current.udtf_scopes:
            collect(sub)
    collect(scope)
    dbcols = database_columns or {}
    cache = {}

    def outputs(current, active=None):
        active = set(active or ())
        if id(current) in active:
            return []
        if id(current) in cache:
            return cache[id(current)]
        active.add(id(current))
        if current.set_operation_scopes:
            branches = [outputs(s, active) for s in current.set_operation_scopes]
            result = []
            for index, item in enumerate(branches[0]):
                result.append({**item, 'alternatives': [v for branch in branches for v in (branch[index]['alternatives'] if index < len(branch) else [])]})
            cache[id(current)] = result
            return result
        if isinstance(current.expression,exp.Values):
            tuples=current.expression.expressions
            aliases=current.outer_columns
            result=[]
            for index in range(len(tuples[0].expressions)):
                alternatives=[]
                for row_index,tuple_ in enumerate(tuples):
                    value=tuple_.expressions[index]
                    kind=literal_kind(value) or {'kind':'nonliteral'}
                    alternatives.append({'expression_sql':value.sql(dialect='duckdb'),'path':str(path),**location(value,text),
                                         **kind,'via':'values_projection','values_row':row_index+1})
                result.append({'name':aliases[index] if index<len(aliases) else f'col{index}', 'alternatives':alternatives})
            cache[id(current)]=result
            return result
        local_sources = current.selected_sources

        def source_outputs(source):
            if isinstance(source, Scope):
                return outputs(source, active)
            if isinstance(source, exp.Table):
                key = canonical_source('.'.join(part.name for part in source.parts))
                return [{'name': name, 'alternatives': []} for name in dbcols.get(key, [])]
            return []

        def resolve(column):
            wanted = column.name.lower()
            options = [(alias, pair[1]) for alias,pair in local_sources.items() if not column.table or alias.lower() == column.table.lower()]
            matches = [item for _, source in options for item in source_outputs(source) if item['name'].lower() == wanted]
            return matches[0]['alternatives'] if len(matches) == 1 else []

        result = []
        for projection in current.expression.expressions:
            bare = projection.unalias()
            if isinstance(bare, exp.Star) or isinstance(bare, exp.Column) and isinstance(bare.this, exp.Star):
                excluded = {n.name.lower() for n in bare.find_all(exp.Identifier)} if isinstance(bare, exp.Star) else set()
                for alias, (_, source) in local_sources.items():
                    if isinstance(bare, exp.Column) and bare.table and bare.table.lower() != alias.lower():
                        continue
                    result.extend(item for item in source_outputs(source) if item['name'].lower() not in excluded)
                continue
            name = projection.alias if isinstance(projection,exp.Alias) else projection.name if isinstance(projection,exp.Column) else projection.sql(dialect='duckdb')
            kind = literal_kind(projection)
            base = {'expression_sql': bare.sql(dialect='duckdb'), 'path': str(path), **location(projection,text)}
            if kind:
                alternatives = [{**base, **kind, 'via': 'literal_projection'}]
            elif isinstance(bare, exp.Column):
                inherited = resolve(bare)
                alternatives = [{**v, 'via': 'column_reference_to_literal_projection', 'outer_expression_sql': base['expression_sql'],
                                 'outer_line': base['line']} for v in inherited] or [{**base,'kind':'nonliteral'}]
            else:
                alternatives = [{**base,'kind':'nonliteral'}]
            result.append({'name': name, 'alternatives': alternatives})
        cache[id(current)] = result
        return result
    projections = outputs(scope)
    return {'path': str(path), 'status':'parsed', 'parser':sqlglot.__version__, 'sources':list(sources.values()),
            'unresolved_source_expressions':unresolved,'row_generator_expressions':generators,'outputs':projections,
            'null_literal_outputs':[o for o in projections if any(a['kind']=='null_literal' for a in o['alternatives'])],
            'constant_literal_outputs':[o for o in projections if any(a['kind']=='nonnull_literal' for a in o['alternatives'])],
            'runtime_hits':runtime_hits(text,path,sql=True)}


def profile_table(connection, schema, table, blocks):
    """Use signatures only to prune; confirm every equal-column group exactly."""
    relation = quote(schema) + '.' + quote(table)
    columns = connection.execute('SELECT column_name,data_type FROM information_schema.columns WHERE table_catalog=current_database() AND table_schema=? AND table_name=? ORDER BY ordinal_position',[schema,table]).fetchall()
    if not columns:
        return {'status':'table_missing', 'exists':False, 'row_count':None, 'zero_rows':None,
                'all_null_columns':None, 'constant_nonnull_columns':None, 'equal_column_groups':None}
    expressions = ['count(*)']
    for name,_ in columns:
        value = 'CAST(' + quote(name) + ' AS VARCHAR)'
        expressions.extend(['count('+quote(name)+')', 'min('+value+')', 'max('+value+')', 'sum(hash('+value+'))'])
    profile_sql = 'SELECT ' + ','.join(expressions) + ' FROM ' + relation
    values = connection.execute(profile_sql).fetchone()
    count = values[0]
    all_null, constants, groups, profiles = [], [], defaultdict(list), []
    for index,(name,kind) in enumerate(columns):
        nonnull, low, high, signature = values[1+4*index:5+4*index]
        profiles.append({'name':name,'type':kind,'nonnull_rows':nonnull,'sql_null_rows':count-nonnull})
        if count and not nonnull:
            all_null.append({'column':name, 'table_rows':count})
        if count > 1 and nonnull == count and low == high:
            constants.append({'column':name,'type':kind,'value':low,'value_representation':'DuckDB CAST AS VARCHAR, exact, no normalization',
                              'table_rows':count,'contract':column_contract(blocks,name)})
        if nonnull:
            groups[(nonnull,low,high,signature)].append(name)
    equal_groups, exact_queries = [], []
    for names in groups.values():
        if len(names) < 2:
            continue
        confirmed = []
        for name in names:
            placed = False
            for group in confirmed:
                left,right=quote(group[0]),quote(name)
                sql = f'SELECT count(*) FILTER(WHERE CAST({left} AS VARCHAR) IS DISTINCT FROM CAST({right} AS VARCHAR)),count(*) FILTER(WHERE {left} IS NOT NULL AND {right} IS NOT NULL AND CAST({left} AS VARCHAR)=CAST({right} AS VARCHAR)) FROM {relation}'
                mismatch, nonnull_equal = connection.execute(sql).fetchone()
                exact_queries.append({'left':group[0],'right':name,'sql':sql,'mismatch_rows':mismatch,'nonnull_equal_rows':nonnull_equal})
                if mismatch == 0 and nonnull_equal > 0:
                    group.append(name);placed=True;break
            if not placed:
                confirmed.append([name])
        for group in confirmed:
            if len(group) < 2:
                continue
            specs={c:column_contract(blocks,c) for c in group}
            description_pairs=[]
            for a,b in combinations(group,2):
                da=[d['description'] for d in specs[a]['definitions'] if d['description']]
                db=[d['description'] for d in specs[b]['definitions'] if d['description']]
                description_pairs.append({'left':a,'right':b,'both_have_explicit_descriptions':bool(da and db),
                    'description_texts_differ':bool(da and db and da!=db), 'semantic_equivalence_evaluated':False})
            nonnull=next(p['nonnull_rows'] for p in profiles if p['name']==group[0])
            equal_groups.append({'columns':group,'table_rows':count,'nonnull_equal_rows':nonnull,
                'both_null_rows_ignored':count-nonnull,'mismatch_rows':0,'column_contracts':specs,
                'description_pairs':description_pairs,'has_pair_with_different_explicit_description':any(p['description_texts_differ'] for p in description_pairs),
                'meaning_status':'description_texts_differ_no_semantic_judgment' if any(p['description_texts_differ'] for p in description_pairs) else '契约未描述含义差别'})
    return protect_constant_values({'status':'checked','exists':True,'row_count':count,'zero_rows':count==0,'columns':profiles,
            'all_null_columns':all_null,'constant_nonnull_columns':constants,'equal_column_groups':equal_groups,
            'profile_sql':profile_sql,'equal_column_confirmation_queries':exact_queries,
            'equality_policy':'exact CAST AS VARCHAR per row; no trim/case/numeric/date normalization; both NULL ignored; at least one nonnull equal row; one-sided NULL differs'})
