from string import Template

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
                  WHERE a.italian = b.italian_no_article OR a.lemma_forms = b.italian_no_article)
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
  def get(self):
    ###################
    # Setup
    ###################
    # Model information
    source_table = 'vocabulary_enriched'
    source_columns = ['italian', 'english', 'part_of_speech', 'wiktionary_rank', 'it_2012_occurrences']

    # Convenient access to request arguments
    rargs = request.args

    ###################
    # Build query
    ###################
    # Base query
    select_clause = 'SELECT %s' % ','.join(source_columns)
    from_clause = 'FROM %s' % source_table

    # Paging
    limit_clause = ''
    iDisplayStart = rargs.get('iDisplayStart', type=int)
    iDisplayLength = rargs.get('iDisplayLength', type=int)
    if (iDisplayStart is not None and iDisplayLength  != -1):
      limit_clause = 'LIMIT %d OFFSET %d' % (iDisplayLength, iDisplayStart)

    # Sorting
    # TODO(hammer): use NULLS FIRST/NULLS LAST to get int-None sorting behavior
    iSortingCols = rargs.get('iSortingCols', type=int)
    orders = ['%s %s' % (source_columns[rargs.get('iSortCol_%d' % i, type=int)],
                         'ASC' if rargs.get('sSortDir_%d' % i) == 'asc' else 'DESC')
              for i in range(iSortingCols)
              if rargs.get('bSortable_%d' % rargs.get('iSortCol_%d' % i, type=int), type=bool)]
    order_clause = 'ORDER BY %s' % ','.join(orders) if orders else ''

    # Filtering
    # TODO(hammer): implement per-column filtering
    where_clause = ''
    sSearch = rargs.get('sSearch')
    if sSearch:
      where_clause = 'WHERE (%s)' % ' OR '.join([Template("CAST($col AS text) LIKE %s").safe_substitute(dict(col=col))
                                                 for col
                                                 in source_columns])

    sql = ' '.join([select_clause, from_clause, where_clause, order_clause, limit_clause]) + ';'

    ###################
    # Execute query
    ###################
    cursor = get_database_connection().cursor()
    # safe string substitution
    if where_clause:
      cursor.execute(sql, ('%' + sSearch + '%',) * len(source_columns))
    else:
      cursor.execute(sql)
    things = cursor.fetchall()

    ###################
    # Assemble response
    ###################
    sEcho = rargs.get('sEcho', type=int)

    # TODO(hammer): don't do 3 queries!
    # Count of all values in table
    cursor.execute(' '.join(['SELECT COUNT(*)', from_clause]) + ';')
    iTotalRecords = cursor.fetchone()[0]

    # Count of all values that satisfy WHERE clause
    iTotalDisplayRecords = iTotalRecords
    if where_clause:
      sql = ' '.join([select_clause, from_clause, where_clause]) + ';'
      cursor.execute(sql, ('%' + sSearch + '%',) * len(source_columns))
      iTotalDisplayRecords = cursor.rowcount

    response = {'sEcho': sEcho,
                'iTotalRecords': iTotalRecords,
                'iTotalDisplayRecords': iTotalDisplayRecords,
                'aaData': things
               }

    return response


api.add_resource(Vocabulary, '/vocabulary')

