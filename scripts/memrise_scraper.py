#! /usr/bin/env python3
import argparse
from collections import namedtuple
import configparser
from itertools import zip_longest
import logging
import json
import os
import re
from urllib.parse import urljoin

import jsonpath_rw as jp
from lxml import html
import requests


# Constants
# JH: not sure why the CSRF token is required, but can't get logins to work without it.
DELIMITER = '|'
CSRFTOKEN = 'a'
CONFIGURATION_FILE = 'memrise_scraper.ini'
CONFIGURATION_SECTION = 'memrise.com'
LOGIN_URL = 'https://www.memrise.com/login/'
ITALIAN_COURSES_URL = 'http://www.memrise.com/ajax/courses/dashboard/?courses_filter=learning&category_id=5'
LEVEL_URL_BASE = 'http://www.memrise.com/ajax/level/editing_html/?level_id='
JP_COURSES = 'courses[*].(id|name|url)'

# Types
Course = namedtuple('Course', ['id', 'name', 'url', 'terms'])
Term = namedtuple('Term', ['italian', 'english', 'pos', 'gender'])


# Utility functions
# Thanks https://docs.python.org/3.5/library/itertools.html#itertools-recipes
def grouper(iterable, n, fillvalue=None):
  "Collect data into fixed-length chunks or blocks"
  # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
  args = [iter(iterable)] * n
  return zip_longest(*args, fillvalue=fillvalue)


# Script functions
def parse_terms(rendered):
  XPATH_THINGS = '//tr[@class="thing"]'
  XPATH_FIELDS = 'td[starts-with(@class, "cell text")]/div/div'
  tree = html.fromstring(rendered)
  things = tree.xpath(XPATH_THINGS)
  terms = []
  for thing in things:
    fields = thing.xpath(XPATH_FIELDS)
    # some old courses return the sound column; need a better solution
    if len(fields) == 5: del fields[2]
    italian = fields[0].text
    english = fields[1].text
    pos = fields[2].text if fields[2].text is not None else ''
    gender = fields[3].text if len(fields) > 3 and fields[3].text is not None else ''
    terms.append(Term(italian, english, pos, gender))
  return terms

def fetch_content(username, password):
  login_data = dict(username=username, password=password, csrfmiddlewaretoken=CSRFTOKEN)
  headers = {'Referer': 'https://www.memrise.com'} # needed for HTTPS for some reason
  cookie_data = {'csrftoken': CSRFTOKEN}

  session = requests.session()
  logging.info('Sending login POST')
  session.post(LOGIN_URL, data=login_data, cookies=cookie_data, headers=headers)

  # Get Italian courses
  logging.info('Sending courses GET')
  req = session.get(ITALIAN_COURSES_URL)
  courses_json = json.loads(req.text)
  courses_data = [match.value for match in jp.parse(JP_COURSES).find(courses_json)]
  courses = [Course(id, name, url, []) for id, name, url in grouper(courses_data, 3)]

  for course in courses:
    # Get levels
    req = session.get(urljoin(course.url, 'edit'))
    tree = html.fromstring(req.text)
    levels = tree.xpath('//@data-level-id')
    # need to clean up levels
    list(set([int(re.findall(r'\d+', level)[0]) for level in levels]))
    for level in levels:
      req = session.get(LEVEL_URL_BASE + str(level))
      resp_json = json.loads(req.text)
      terms = parse_terms(resp_json['rendered'])
      course.terms.extend(terms)

  # Flatten data and write to TSV
  with open('memrise.tsv', 'w') as outfile:
    fields = ['Course', 'Italian', 'English', 'POS', 'Gender']
    outfile.write(DELIMITER.join(fields) + '\n')
    for course in courses:
      for term in course.terms:
        tokens = [course.name, term.italian, term.english, term.pos, term.gender]
        outfile.write(DELIMITER.join(tokens) + '\n')


if __name__ == "__main__":
  # First, look for configuration parameters in the environment
  username = os.environ.get('MEMRISE_USERNAME', '')
  password = os.environ.get('MEMRISE_PASSWORD', '')

  # Second, look for configuration parameters in a configuration file (in this directory)
  config = configparser.ConfigParser()
  config.read(CONFIGURATION_FILE)
  if config.has_section(CONFIGURATION_SECTION):
    config_dict = config[CONFIGURATION_SECTION]
    username = config_dict.get('username', username)
    password = config_dict.get('password', password)

  # Third, look for configuration parameters on the command line
  parser = argparse.ArgumentParser(description='Scrape vocabulary from Memrise.')
  parser.add_argument('-u', '--username')
  parser.add_argument('-p', '--password')
  parser.add_argument('-v', '--verbose', action='store_true')
  args = parser.parse_args()
  if args.username is not None: username = args.username
  if args.password is not None: password = args.password
  if args.verbose: logging.basicConfig(level=logging.DEBUG)

  # Do some work
  logging.info('Fetching content for username %s with password %s' % (username, password))
  fetch_content(username, password)



