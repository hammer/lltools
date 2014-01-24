from setuptools import setup

setup(
    name='memrise_scraper',
    version='0.1',
    long_description=__doc__,
    packages=['memrise_scrape_viewer'],
    scripts=['scripts/memrise_scraper.py', 'scripts/run_memrise_scrape_viewer_server.py'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask', 'flask-restful', 'psycopg2', 'requests', 'lxml']
)

