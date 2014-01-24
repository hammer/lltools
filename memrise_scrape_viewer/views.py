from string import Template
from distutils.util import strtobool

from flask import g, render_template, request
from flask.ext.restful import Resource, Api
import psycopg2
from psycopg2.extras import RealDictCursor

from memrise_scrape_viewer import app

# Flask-RESTful object; maybe better in __init__.py?
api = Api(app)


# Configuration
DATABASE_NAME = 'memrise'
DEBUG = True


# Helper functions for interacting with the database
def connect_to_database():
  return psycopg2.connect("dbname=%s" % DATABASE_NAME)

def get_database_connection():
  database = getattr(g, '_database', None)
  if database is None:
    database = g._database = connect_to_database()
  return database

@app.teardown_appcontext
def close_connection(exception):
  database = getattr(g, '_database', None)
  if database is not None:
    database.close()


# Routes
@app.route('/')
def index():
  cursor = get_database_connection().cursor(cursor_factory=RealDictCursor)

  # Retrieve unknown words from the Wiktionary frequency list
  cursor.execute("""\
SELECT *
FROM frequency_wiktionary a
WHERE NOT EXISTS (SELECT 1
                  FROM vocabulary b
                  WHERE a.italian = b.italian_no_article
                        OR a.lemma_forms = b.italian_no_article)
      AND char_length(a.italian) > 2;
""")
  wiktionary_unknown_words = cursor.fetchall()

  # Retrieve unknown words from the it 2012 frequency list
  cursor.execute("""\
SELECT *
FROM frequency_it_2012 a
WHERE NOT EXISTS (SELECT 1
                  FROM vocabulary b
                  WHERE a.italian = b.italian_no_article)
      AND char_length(a.italian) > 2
LIMIT 1000;
""")
  it_2012_unknown_words = cursor.fetchall()

  # Render template
  return render_template('index.html',
                         wiktionary_unknown_words=wiktionary_unknown_words,
                         it_2012_unknown_words=it_2012_unknown_words)

# API endpoint for vocabulary table, since it's getting big
class Vocabulary(Resource):
  def post(self):
    conn = get_database_connection()
    cursor = conn.cursor()
    source_table = 'vocabulary_deduplicated'
    source_columns = ['italian', 'english', 'part_of_speech', 'course',
                      'wiktionary_rank', 'it_2012_occurrences']

    # Delete
    if request.form.get('delete', type=strtobool):
      oid = request.form.get('row_id', type=int)
      table_sql = 'DELETE FROM %s' % source_table
      cursor.execute(table_sql + ' WHERE oid = %s;', (oid,))
      conn.commit()
      return

    # Update
    oid = request.form.get('row_id', type=int)
    column = request.form.get('column', type=int)
    column_name = source_columns[column]
    value = request.form.get('value')

    table_col_sql = 'UPDATE %s SET %s' % (source_table, column_name)
    cursor.execute(table_col_sql + ' = %s WHERE oid = %s;', (value, oid))
    conn.commit()

    return value

  def get(self):
    ###################
    # Setup
    ###################
    # Model information
    cursor = get_database_connection().cursor(cursor_factory=RealDictCursor)
    source_table = 'vocabulary_deduplicated'
    source_columns = ['italian', 'english', 'part_of_speech', 'course',
                      'wiktionary_rank', 'it_2012_occurrences',
                      'oid AS "DT_RowId"']
    display_columns = ['delete', 'italian', 'english', 'part_of_speech', 'course',
                       'wiktionary_rank', 'it_2012_occurrences']

    ###################
    # Build query
    ###################
    # Convenient access to request arguments
    rargs = request.args

    # Base query
    select_clause = 'SELECT %s' % ','.join(source_columns)
    from_clause = 'FROM %s' % source_table

    # Paging
    iDisplayStart = rargs.get('iDisplayStart', type=int)
    iDisplayLength = rargs.get('iDisplayLength', type=int)
    limit_clause = 'LIMIT %d OFFSET %d' % (iDisplayLength, iDisplayStart) \
                   if (iDisplayStart is not None and iDisplayLength  != -1) \
                   else ''

    # Sorting
    iSortingCols = rargs.get('iSortingCols', type=int)
    orders = []
    for i in range(iSortingCols):
      col_index = rargs.get('iSortCol_%d' % i, type=int)
      if rargs.get('bSortable_%d' % col_index, type=strtobool):
        col_name = display_columns[col_index]
        sort_dir =  'ASC' \
                    if rargs.get('sSortDir_%d' % i) == 'asc' \
                    else 'DESC NULLS LAST'
        orders.append('%s %s' % (col_name, sort_dir))
    order_clause = 'ORDER BY %s' % ','.join(orders) if orders else ''

    # Filtering ("ac" is "all columns", "pc" is "per column")
    ac_search = rargs.get('sSearch')
    ac_like_exprs, ac_patterns, pc_like_exprs, pc_patterns = [], [], [], []
    for i, col in enumerate(display_columns):
      if rargs.get('bSearchable_%d' % i, type=strtobool):
        like_expr = Template("$col LIKE %s").safe_substitute(dict(col=col))
        if ac_search:
          ac_like_exprs.append(like_expr)
          ac_patterns.append('%' + ac_search + '%')

        pc_search = rargs.get('sSearch_%d' % i)
        if pc_search:
          pc_like_exprs.append(like_expr)
          pc_patterns.append('%' + pc_search + '%')

    ac_subclause = '(%s)' % ' OR '.join(ac_like_exprs) if ac_search else ''
    pc_subclause = ' AND '.join(pc_like_exprs)
    subclause = ' AND '.join([ac_subclause, pc_subclause]) \
                if ac_subclause and pc_subclause \
                else ac_subclause or pc_subclause
    where_clause = 'WHERE %s' % subclause if subclause else ''

    sql = ' '.join([select_clause,
                    from_clause,
                    where_clause,
                    order_clause,
                    limit_clause]) + ';'

    ###################
    # Execute query
    ###################
    cursor.execute(sql, ac_patterns + pc_patterns)
    things = cursor.fetchall()
    # Feels cleaner to do this here and not with source_columns
    [thing.update({'delete':''}) for thing in things]

    ###################
    # Assemble response
    ###################
    sEcho = rargs.get('sEcho', type=int)

    # TODO(hammer): don't do 3 queries!
    # Count of all values in table
    cursor.execute(' '.join(['SELECT COUNT(*)', from_clause]) + ';')
    iTotalRecords = cursor.fetchone().get('count')

    # Count of all values that satisfy WHERE clause
    iTotalDisplayRecords = iTotalRecords
    if where_clause:
      sql = ' '.join([select_clause, from_clause, where_clause]) + ';'
      cursor.execute(sql, ac_patterns + pc_patterns)
      iTotalDisplayRecords = cursor.rowcount

    response = {'sEcho': sEcho,
                'iTotalRecords': iTotalRecords,
                'iTotalDisplayRecords': iTotalDisplayRecords,
                'aaData': things
               }
    return response


api.add_resource(Vocabulary, '/vocabulary')
