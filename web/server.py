from flask import Flask, g, render_template
import psycopg2

# Configuration
DATABASE_NAME = 'memrise'
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)


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
  cursor = get_database_connection().cursor()
  cursor.execute("SELECT * FROM vocabulary_duolingo")
  things = cursor.fetchall()

  # Render template
  return render_template('index.html', things=things)


# Main
if __name__ == '__main__':
  app.run()
