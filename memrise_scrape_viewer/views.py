from flask import g, render_template
import psycopg2
from psycopg2.extras import RealDictCursor
from memrise_scrape_viewer import app

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
  # Retrieve list of things from database
  cursor = get_database_connection().cursor(cursor_factory=RealDictCursor)
  cursor.execute("""\
SELECT *
FROM vocabulary_enriched
""")
  things = cursor.fetchall()
  # Don't try this at home, kids
  things = [thing.update({'part_of_speech': thing['part_of_speech'].replace(';','')}) or thing
            for thing in things]

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
                         things=things,
                         wiktionary_unknown_words=wiktionary_unknown_words,
                         it_2012_unknown_words=it_2012_unknown_words)
