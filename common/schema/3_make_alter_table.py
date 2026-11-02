"""
3_make_alter_table.py
For a given table, find differences between old and new schema 
and convert to ALTER TABLE commands
"""
import json
import re
import prims

# A NAMED MySQL INDEX: "UNIQUE KEY one_per_object (diaObjectId, topic)". THE
# PRIMARY KEY IS DELIBERATELY NOT MATCHED -- IT HAS NO NAME TO DROP BY, AND
# REBUILDING ONE IS NOT SOMETHING TO GENERATE UNSEEN. THE COLUMN LIST IS HELD
# TO IDENTIFIER CHARACTERS SO THAT A TYPO -- ANYTHING CARRYING A SEMICOLON OR A
# COMMENT MARKER -- FALLS THROUGH TO MANUAL REVIEW INSTEAD OF BEING COPIED INTO
# GENERATED DDL.
NAMED_INDEX = re.compile(
    r'^(?P<kind>UNIQUE\s+KEY|UNIQUE\s+INDEX|KEY|INDEX)\s+'
    r'`?(?P<name>\w+)`?\s*'
    r'\((?P<columns>[\w\s,`()]+)\)$',
    re.IGNORECASE)


def split_index_entries(indexes: list) -> list:
    """Split an `indexes` list into one clause per entry.

    A single entry may hold several comma-separated clauses, so split on the
    commas that sit outside parentheses.

    Args:
        indexes: the schema's `indexes` list

    Raises:
        ValueError: an entry's parentheses do not balance

    Returns:
        A list of clause strings, whitespace-stripped and never empty
    """
    clauses = []
    for entry in indexes:
        depth = 0
        current = ''
        for character in entry:
            if character == '(':
                depth += 1
            elif character == ')':
                depth -= 1
            if depth < 0:
                raise ValueError('Unbalanced parentheses in index: %s' % entry)
            if character == ',' and depth == 0:
                # A DOUBLED OR LEADING COMMA IS PADDING, NOT AN EMPTY CLAUSE
                if current.strip():
                    clauses.append(current.strip())
                current = ''
            else:
                current += character
        if depth != 0:
            raise ValueError('Unbalanced parentheses in index: %s' % entry)
        if current.strip():
            clauses.append(current.strip())
    return clauses


def collapse(clause: str) -> str:
    """One spelling of a clause, so that two paddings of it compare equal.

    Args:
        clause: an index clause

    Returns:
        The clause with its runs of whitespace collapsed to single spaces
    """
    return ' '.join(clause.split())


def named_indexes(schema: dict) -> tuple:
    """The named indexes of a schema, and the clauses that could not be read.

    Args:
        schema: a table schema dict

    Returns:
        A tuple of `({name: (definition, comparable)}, [unparsed clauses])`,
        where `comparable` ignores backticks and spacing so that two spellings
        of the same index compare equal
    """
    indexes = {}
    unparsed = []
    for clause in split_index_entries(schema.get('indexes', [])):
        match = NAMED_INDEX.match(clause)
        if not match:
            unparsed.append(clause)
            continue
        kind = collapse(match.group('kind').upper())
        columns = [c.strip().strip('`') for c in match.group('columns').split(',')]
        comparable = '%s (%s)' % (kind, ', '.join(columns))
        indexes[match.group('name')] = (clause, comparable)
    return indexes, unparsed


def sql_alter_index(schema_old: dict, schema_new: dict) -> str:
    """ALTER TABLE statements for the indexes that changed between two schemas.

    An index whose columns changed is dropped and re-added in a single
    statement: MySQL cannot redefine one in place, and DDL auto-commits, so
    splitting the two would leave the table with no constraint at all in
    between -- long enough for the live pipeline to write a row that then
    blocks the index from coming back. Adding or changing a UNIQUE index also
    emits the query to run first, because the statement fails outright if the
    live data already holds duplicates. Clauses this cannot read -- the
    PRIMARY KEY above all -- are reported as a comment for a human to act on
    rather than guessed at.

    Args:
        schema_old: the table schema being upgraded from
        schema_new: the table schema being upgraded to

    Returns:
        The statements as one string, empty when no index changed
    """
    tablename = schema_old['name']
    old_indexes, old_unparsed = named_indexes(schema_old)
    new_indexes, new_unparsed = named_indexes(schema_new)

    dropped = [n for n in old_indexes if n not in new_indexes]
    added = [n for n in new_indexes if n not in old_indexes]
    changed = [n for n in new_indexes
               if n in old_indexes and old_indexes[n][1] != new_indexes[n][1]]

    # THE WARNING GOES FIRST. A CLAUSE THAT STOPPED PARSING LOOKS EXACTLY LIKE A
    # DELIBERATELY REMOVED INDEX, SO A READER MUST SEE IT BEFORE ANY DROP BELOW.
    # COMPARED COLLAPSED, SO A REWRAPPED CLAUSE IS NOT REPORTED AS A CHANGE.
    old_loose = set(collapse(c) for c in old_unparsed)
    new_loose = set(collapse(c) for c in new_unparsed)

    lines = ''
    if old_loose != new_loose:
        lines += '-- CHECK BY HAND (%s), not a named index: %s\n' % \
                (tablename, ' / '.join(sorted(old_loose ^ new_loose)))

    for name in sorted(added + changed):
        definition, comparable = new_indexes[name]
        if comparable.startswith('UNIQUE'):
            lines += '-- RUN FIRST, THIS FAILS ON DUPLICATES: SELECT %s, COUNT(*) c ' \
                     'FROM %s GROUP BY %s HAVING c > 1;\n' % \
                    (comparable[comparable.index('(') + 1:-1], tablename,
                     comparable[comparable.index('(') + 1:-1])
    # DROP AND ADD IN ONE STATEMENT, SO A REDEFINED INDEX IS NEVER MISSING
    for name in sorted(changed):
        lines += 'ALTER TABLE %s DROP INDEX %s, ADD %s;\n' % \
                (tablename, name, collapse(new_indexes[name][0]))
    for name in sorted(dropped):
        lines += 'ALTER TABLE %s DROP INDEX %s;\n' % (tablename, name)
    for name in sorted(added):
        lines += 'ALTER TABLE %s ADD %s;\n' % (tablename, collapse(new_indexes[name][0]))
    return lines


# SQL version
def sql_alter_table(schema_old, schema_new):
    tablename = schema_old['name']

    # all the fields from the old schema
    fields_old = schema_old['fields'] + schema_old.get('ext_fields', [])
    attr_old = [f['name'] for f in fields_old if 'name' in f]

    # all the fields from the new schema
    fields_new = schema_new['fields'] + schema_new.get('ext_fields', [])
    attr_new = [f['name'] for f in fields_new if 'name' in f]

    lines = ''
    # What needs to be ADDed to get the new schema
    for f in fields_new:
        if not 'name' in f:       continue
        if f['name'] in attr_old: continue
        lines += 'ALTER TABLE %s ADD `%s` %s;\n' % \
                (tablename, f['name'], prims.sql_type(f['type']))

    # What needs to be DROPped to get the new schema
    for f in fields_old:
        if not 'name' in f:       continue
        if f['name'] in attr_new: continue
        lines += 'ALTER TABLE %s DROP `%s`;\n' % \
                (tablename, f['name'])

    lines += sql_alter_index(schema_old, schema_new)
    return lines

# CQL version
def cql_alter_table(schema_old, schema_new):
    tablename = schema_old['name']

    # all the fields from the old schema
    fields_old = schema_old['fields'] + schema_old.get('ext_fields', [])
    attr_old = [f['name'] for f in fields_old if 'name' in f]

    # all the fields from the new schema
    fields_new = schema_new['fields'] + schema_new.get('ext_fields', [])
    attr_new = [f['name'] for f in fields_new if 'name' in f]

    lines = ''
    # What needs to be ADDed to get the new schema
    for f in fields_new:
        if not 'name' in f:       continue
        if f['name'] in attr_old: continue
        lines += 'ALTER TABLE %s ADD "%s" %s;\n' % \
                (tablename, f['name'], prims.cql_type(f['type']))

    # What needs to be DROPped to get the new schema
    for f in fields_old:
        if not 'name' in f:       continue
        if f['name'] in attr_new: continue
        lines += 'ALTER TABLE %s DROP "%s" ;\n' % \
                (tablename, f['name'])
    return lines

import sys
import importlib
if __name__ == '__main__':
    if len(sys.argv) > 4:
        switch         = sys.argv[1]
        schema_ver_old = sys.argv[2]
        schema_ver_new = sys.argv[3]
        table          = sys.argv[4]
    else:
        print("Usage: 3_make_alter_table.py switch schema_ver_old schema_ver_new table")
        print("Where switch can be sql or cql")
        print("and schema_version can be for example 7_4")
        print("and table is one of objects, sherlock_classifications, etc")
        sys.exit()

    schema_package_old = importlib.import_module('%s.%s' % (schema_ver_old, table))
    schema_old = schema_package_old.schema
    schema_package_new = importlib.import_module('%s.%s' % (schema_ver_new, table))
    schema_new = schema_package_new.schema

    if switch == 'sql':
        lines = sql_alter_table(schema_old, schema_new)
    elif switch == 'cql':
        lines = cql_alter_table(schema_old, schema_new)
    else:
        print('Unknown switch %s' % switch)
    if len(lines) > 0:
        print(lines)
