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
    
  # Retrieve list of things from database
  # (Done by Vocabulary Resource)

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
    # Pull necessary information out of the request object
    rargs = request.args
    sEcho = rargs.get('sEcho', type=int)
    iDisplayStart = rargs.get('iDisplayStart', type=int)
    iDisplayLength = rargs.get('iDisplayLength', type=int)

    # Base query
    select_clause = 'SELECT *' # TODO(hammer): use explicit column names
    from_clause = 'FROM vocabulary_enriched'

    # Paging
    limit_clause = ''
    if (iDisplayStart is not None and iDisplayLength  != -1):
      limit_clause = 'LIMIT %d OFFSET %d' % (iDisplayLength, iDisplayStart)

    # Sorting
    # TODO(hammer): implement
    order_clause = ''

    # Filtering
    # TODO(hammer): implement
    where_clause = ''

    # Build, execute, and retrieve results for query
    sql = ' '.join([select_clause, from_clause, where_clause, order_clause, limit_clause]) + ';'
    cursor = get_database_connection().cursor()
    cursor.execute(sql)
    things = cursor.fetchall()

    # Assemble response
    # TODO(hammer): don't do 3 queries!
    # Count of all values in table
    cursor.execute(' '.join(['SELECT COUNT(*)', from_clause]) + ';')
    iTotalRecords = cursor.fetchone()[0]

    # Count of all values that satisfy WHERE clause
    cursor.execute(' '.join([select_clause, from_clause, where_clause]) + ';')
    iTotalDisplayRecords = cursor.rowcount

    response = {'sEcho': sEcho,
                'iTotalRecords': iTotalRecords,
                'iTotalDisplayRecords': iTotalDisplayRecords,
                'aaData': things
               }

    return response


api.add_resource(Vocabulary, '/vocabulary')

