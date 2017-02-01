from setuptools import setup, find_packages

install_requires = """
    flask
    flask-debugtoolbar
    flask-graphql
    flask-login
    flask-migrate
    flask-shell-ipython
    flask-sqlalchemy

    google-api-python-client
    graphene>=1.0
    graphene_sqlalchemy
    sqlalchemy
    sqlalchemy-utils

    furl
    python-dateutil
    pyyaml

    future
""".split()

tests_require = """
    flask-fixtures
    flask-testing
    nose
""".split()

setup(
    name="bitsbox",
    packages=find_packages(),
    include_package_data=True,

    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='nose.collector',
)
