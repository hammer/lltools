from lxml import html
import requests

# User-supplied configuration
USERNAME = ''
PASSWORD = ''
DATABASE = ''

# Constants
# JH: not sure why the CSRF token is required, but can't get logins to work without it.
CSRFTOKEN = 'a'
LOGIN_URL = 'http://www.memrise.com/login/'
FIELD_SEPARATOR = '|' 


def fetch_content():
  XPATH_PAGINATION = '//div[starts-with(@class, "pagination")]/ul/li/a/text()'

  login_data = dict(username=USERNAME, password=PASSWORD, csrfmiddlewaretoken=CSRFTOKEN)
  cookie_data = {'csrftoken': CSRFTOKEN}

  session = requests.session()
  session.post(LOGIN_URL, data=login_data, cookies=cookie_data)

  page_number = 0
  while (True):
    page_number += 1
    req = session.get(DATABASE + '?page=%d' % page_number)
    this_page = req.text

    with open('page%s.html' % page_number, 'w') as ofile:
      ofile.write(this_page)

    # Detect if we're at the end of a database
    if 'Next' not in html.fromstring(this_page).xpath(XPATH_PAGINATION)[-1]:
      break


def parse_content():
  XPATH_THINGS = '//tr[@class="thing"]'
  XPATH_FIELDS = 'td[starts-with(@class, "cell text")]/div/div'

  page_number = 0
  all_things = []
  while (True):
    page_number += 1
    try:
      with open('page%s.html' % page_number) as infile:
        tree = html.fromstring(infile.read())
        things = tree.xpath(XPATH_THINGS)
        for thing in things:
          fields = thing.xpath(XPATH_FIELDS)
          all_things.append([field.text if field.text else '' for field in fields])
    except:
      break

  # TODO(hammer): escape field separator
  with open('all_things.csv', 'w') as ofile:
    ofile.write('\n'.join([FIELD_SEPARATOR.join(thing) for thing in all_things]))


if __name__ == "__main__":
  fetch_content()
  parse_content()


