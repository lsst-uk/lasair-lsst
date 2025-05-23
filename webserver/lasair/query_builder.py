"""
Lasair Query Builder
These functions are to convert a user's query int sanitised SQL that can run on the database.
The SQL looks like
    SELECT <select_expression>
    FROM <from_expression>
    WHERE <where_condition>
Note that this part of query is added outside of this code
    LIMIT <limit> OFFSET <offset>
Example:
    select_expression = 'diaObjectId'
    from_expression   = 'objects'
    where_condition   = 'mag < 14 ORDER BY maxTai'
The syntax checking happens in two stages, first in this code and then in the SQL engine.
The limit and offset are checked here that they are integers.

The select_expression and where conditions are checked for forbidden characters
and words that could be used for injection attacks on Lasair,
or that indicate the user is not understanding what to do, and the input
rejected if these are found, with an error message returned.
"""
import json
import random
import string
import re
from src import db_connect
import settings
import sys
sys.path.append('../../../common')
max_execution_time = 300000  # maximum execution time in milliseconds
max_query_rows = 1000    # default LIMIT if none specified


class QueryBuilderError(Exception):
    """ Thrown when parsing encounters an error
    """

    def __init__(self, message):
        self.message = message


# These strings have no reason to be in the query
forbidden_string_list = ['#', '/*', '*/', ';', '||', '\\']

# These words have no reason to be in the select_expression
select_forbidden_word_list = [
    'create',
    'select', 'from', 'where', 'join', 'inner', 'outer', 'with',
    'high_priority', 'straight_join',
    'sql_small_result', 'sql_big_result', 'sql_buffer_result',
    'sql_no_cache', 'sql_calc_found_rows',
    'sleep',
]


def check_select_forbidden(select_expression):
    """ Check the select expression for bad things
    """
    # This field cannot be blank, or the SQL will be SELECT FROM which is wrong.
    if len(select_expression.strip()) == 0:
        return('SELECT expression cannot be blank. Try putting * in it.')

    # Check no forbidden strings
    for s in forbidden_string_list:
        if select_expression.find(s) >= 0:
            return ('Cannot use %s in the SELECT clause' % s)

    # Want to split on whitespace, parentheses, curlys
    se = re.split('\\s|\(|\)|\{|\}', select_expression.lower())

    # Check no forbidden words
    for s in select_forbidden_word_list:
        if s in se or s.upper() in se:
            return ('Cannot use the word %s in the SELECT clause' % s.upper())
    return None


# These words have no reason to be in the where_condition
where_forbidden_word_list = [
    'create',
    'select', 'union', 'exists', 'window',
    #    'having', 'group', 'groupby',    # until after broker workshop
    'for',
    'into', 'outfile', 'dumpfile',
]


def check_where_forbidden(where_condition):
    """ Check the select expression for bad things
    """
    if not where_condition:
        return None
    # Check no forbidden strings
    for s in forbidden_string_list:
        if where_condition and where_condition.find(s) >= 0:
            return('Cannot use %s in the WHERE clause' % s)

    # REMOVE COMMENTS
    if where_condition:
        regex = re.compile(r'^\S*\-+\s*.*')
        where_condition = regex.sub("", where_condition)

    # Want to split on whitespace, parentheses, curlys
    wc = re.split('\\s|\(|\)|\{|\}', where_condition.lower())
    for w in where_forbidden_word_list:
        if w in wc or w.upper() in wc:
            return('Cannot use the word %s in the WHERE clause' % w.upper())

    # Check they havent put LIMIT or OFFSET in where_condition, they should be elsewhere
    if where_condition.find('limit') >= 0:
        return('Dont put LIMIT in the WHERE clause, use the parameter in the form/API instead')
    if where_condition.find('offset') >= 0:
        return('Dont put OFFSET in the WHERE clause, use the parameter in the form/API instead')

    return None


def check_query(select_expression, from_expression, where_condition):
    """ Check the query arguments with the functions above
    """
    # check if the select expression is OK
    s = check_select_forbidden(select_expression)
    if s:
        return s

    # check if the where conditions is OK
    s = check_where_forbidden(where_condition)
    if s:
        return s

    return None


def sanitise(expression):
    return expression.replace("'", '"')


def build_query(select_expression, from_expression, where_condition):
    """ Build a real SQL query from the pre-sanitised input
    """
    if select_expression:
        select_expression = sanitise(select_expression)
    if where_condition:
        where_condition = sanitise(where_condition)

    select_expression = select_expression.replace("objects_ext", "objects")
    from_expression = from_expression.replace("objects_ext", "objects")
    if where_condition:
        where_condition = where_condition.replace("objects_ext", "objects")

    # ----- Handle the from_expression.
    # This is a comma-separated list, of very restricted form
    # Implicitly includes 'objects', dont care if they includid it or not.
    # Can include 'sherlock_classifications' and 'tns_crossmatch' and 'annotations'
    # Can include 'watchlists:nnn' and 
    # 'areas:nnn' or watchmaps:nnn where nnn is an integer.
    # Cannot have both watchlist and crossmatch_tns (the latter IS a watchlist)

    sherlock_classifications = False  # using sherlock_classifications
    crossmatch_tns = False  # using crossmatch tns, but not combined with watchlist
    annotation_topics = []  # topics of chosen annotations
    watchlist_id = None     # wl_id of the chosen watchlist, if any
    area_ids = None     # wl_id of the chosen watchlist, if any

    tables = from_expression.split(',')
    for _table in tables:
        table = _table.strip().lower()

        if table == 'sherlock_classifications':
            sherlock_classifications = True

        if table.startswith('watchlist:'):
            w = table.split(':')
            try:
                watchlist_id = int(w[1])
            except:
                raise QueryBuilderError('Error in FROM list, %s not of the form watchlist:nnn' % table)

        if table.startswith('area:') or table.startswith('watchmap:'):
            w = table.split(':')
            try:
                area_ids = w[1].split('&')
            except:
                raise QueryBuilderError('Error in FROM list, %s not of the form area:nnn or watchmap:nnn' % table)

        # multiple annotations comes in here from web as annotator:apple&pear
        # comes in from API/client as annotator:apple, annotator:pear
        if table.startswith('annotator'):
            w = table.split(':')
            try:
                annotation_topics += w[1].split('&')
            except:
                raise QueryBuilderError('Error in FROM list, %s not of the form annotation:topic' % table)

    # We know if the watchlist is there or n ot, can see if the put in crossamtch_tns
    for _table in tables:
        table = _table.strip().lower()
        if table == 'crossmatch_tns':
            if watchlist_id:
                raise QueryBuilderError('Error in FROM list, cannot have both watchlist and crossmatch_tns')
            crossmatch_tns = True

    # List of tables
    from_table_list = ['objects']
    if sherlock_classifications:
        from_table_list.append('sherlock_classifications')
    if watchlist_id:
        from_table_list.append('watchlist_hits')
    if area_ids:
        if len(area_ids) == 1:
            from_table_list.append('area_hits')
        else:
            for i, a in enumerate(area_ids):
                from_table_list.append(f'area_hits as ar{i}')

    if crossmatch_tns:
        from_table_list.append('watchlist_hits')
        from_table_list.append('crossmatch_tns')
    if annotation_topics:
        for at in annotation_topics:
            from_table_list.append('annotations AS ' + at)

    # Extra clauses of the WHERE expression to make the JOINs
    where_clauses = []
    if sherlock_classifications:
        where_clauses.append('objects.diaObjectId=sherlock_classifications.diaObjectId')
    if watchlist_id:
        where_clauses.append('objects.diaObjectId=watchlist_hits.diaObjectId')
        where_clauses.append('watchlist_hits.wl_id=%s' % watchlist_id)
    if area_ids:
        if len(area_ids) == 1:
            where_clauses.append('objects.diaObjectId=area_hits.diaObjectId')
            where_clauses.append(f'area_hits.ar_id={area_ids[0]}')
        else:
            for i, a in enumerate(area_ids):
                where_clauses.append(f'objects.diaObjectId=ar{i}.diaObjectId')
                where_clauses.append(f'ar{i}.ar_id={a}')
    if crossmatch_tns:
        where_clauses.append('objects.diaObjectId=watchlist_hits.diaObjectId')

        where_clauses.append('watchlist_hits.wl_id=%d' % settings.TNS_WATCHLIST_ID)
        where_clauses.append('watchlist_hits.name=crossmatch_tns.tns_name')

    if len(annotation_topics) > 0:
        for at in annotation_topics:
            where_clauses.append('objects.diaObjectId=%s.diaObjectId' % at)
            where_clauses.append('%s.topic="%s"' % (at, at))

    # if the WHERE is just an ORDER BY, then we mustn't have AND before it
    order_condition = ''
    if where_condition:
        if where_condition.lower().strip().startswith('order'):
            order_condition = ' ' + where_condition
        else:
            if len(where_condition.strip()) > 0:
                where_clauses.append(where_condition)

    # Now we can build the real SQL
    sql = 'SELECT ' + select_expression

    # FROM these tables
    sql += ' \nFROM ' + ', '.join(from_table_list)

    # The WHERE clauses
    if len(where_clauses) > 0:
        sql += ' \nWHERE\n ' + ' AND\n '.join(where_clauses)

    # order condition if any
    sql += order_condition

    return sql


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        mq_id = int(sys.argv[1])
    else:
        print('Usage: "python query_builder.py 123" for mq_id=123')
        sys.exit(1)

    msl = db_connect.remote()
    query = 'SELECT selected, conditions, tables FROM myqueries WHERE mq_id=%d'
    query = query % mq_id
    cursor = msl.cursor(buffered=True, dictionary=True)
    cursor.execute(query)
    for row in cursor:
        s = row['selected']
        f = row['tables']
        w = row['conditions']
        break

    e = check_query(s, f, w)
    if e:
        print(e)
    else:
        real_sql = build_query(s, f, w)
        print(real_sql)
    print('-----------------')
    query = "UPDATE myqueries SET real_sql='%s' WHERE mq_id=%d" % (real_sql, mq_id)
    cursor.execute(query)
