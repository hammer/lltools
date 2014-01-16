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
SELECT b.italian, a.english, a.part_of_speech, b.rank
FROM vocabulary_duolingo a
LEFT OUTER JOIN frequency_wiktionary b
ON (a.italian_no_article=b.italian);
""")
  things = cursor.fetchall()
  # Don't try this at home, kids
  things = [thing.update({'part_of_speech': thing['part_of_speech'].replace(';','')}) or thing
            for thing in things]

  # Retrieve unknown words from the frequency list
  cursor.execute("""\
SELECT *
FROM frequency_wiktionary a
WHERE NOT EXISTS (SELECT 1 
                  FROM vocabulary_duolingo b 
                  WHERE a.italian = b.italian_no_article OR a.lemma_forms = b.italian_no_article)
      AND char_length(a.italian) > 2;
""")
  unknown_words = cursor.fetchall()

  # Render template
  return render_template('index.html', things=things, unknown_words=unknown_words)
