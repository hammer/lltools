from setuptools import setup

setup(
    name='lltools',
    version='0.1',
    long_description=__doc__,
    packages=['lltools_web'],
    scripts=['scripts/memrise_scraper.py', 'scripts/run_lltools_web.py'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['flask', 'flask-restful', 'psycopg2', 'requests', 'lxml']
)

