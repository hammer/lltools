import configparser
import logging
from lxml import html
import requests

# Constants
# JH: not sure why the CSRF token is required, but can't get logins to work without it.
CSRFTOKEN = 'a'
LOGIN_URL = 'http://www.memrise.com/login/'
FIELD_SEPARATOR = '|'
CONFIGURATION_FILE = 'memrise_scraper.ini'

# Set logging level
# TODO(hammer): allows this to be configurable with -v/--verbose command line flag
logging.basicConfig(level=logging.DEBUG)


def parse_configuration(configuration_file=CONFIGURATION_FILE):
  config = configparser.ConfigParser()
  config.read('memrise_scraper.ini')
  return config['DEFAULT']['username'], config['DEFAULT']['password'], config['DEFAULT']['databases'].split(',')


def fetch_content(username, password, databases):
  XPATH_PAGINATION = '//div[starts-with(@class, "pagination")]/ul/li/a/text()'

  login_data = dict(username=username, password=password, csrfmiddlewaretoken=CSRFTOKEN)
  cookie_data = {'csrftoken': CSRFTOKEN}

  session = requests.session()
  session.post(LOGIN_URL, data=login_data, cookies=cookie_data)

  for database_number, database in enumerate(databases, 1):
    page_number = 0
    while (True):
      page_number += 1
      logging.info('Processing database %s, page %d' % (database, page_number))
      req = session.get(database + '?page=%d' % page_number)
      this_page = req.text

      with open('database%dpage%d.html' % (database_number, page_number), 'wt') as ofile:
        ofile.write(this_page)

      # Detect if we're at the end of a database
      if 'Next' not in html.fromstring(this_page).xpath(XPATH_PAGINATION)[-1]:
        break


def parse_content():
  XPATH_THINGS = '//tr[@class="thing"]'
  XPATH_FIELDS = 'td[starts-with(@class, "cell text")]/div/div'

  database_number = 0
  while (True):
    database_number += 1
    page_number = 0
    all_things = []
    while (True):
      page_number += 1
      logging.info('Processing database %s, page %d' % (database_number, page_number))
      try:
        with open('database%dpage%d.html' % (database_number, page_number)) as infile:
          tree = html.fromstring(infile.read())
          things = tree.xpath(XPATH_THINGS)
          for thing in things:
            fields = thing.xpath(XPATH_FIELDS)
            all_things.append([field.text if field.text else '' for field in fields])
      except:
        break

    # Indicates that we've read the last database
    if page_number == 1:
      break

    # TODO(hammer): escape field separator
    with open('database%d.csv' % database_number, 'wt') as ofile:
      ofile.write('\n'.join([FIELD_SEPARATOR.join(thing) for thing in all_things]))


if __name__ == "__main__":
  username, password, databases = parse_configuration()
  fetch_content(username, password, databases)
  parse_content()


