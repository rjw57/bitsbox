from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

from .ui import blueprint as ui
from .graphql import (
    graphql_blueprint as graphql,
    graphiql_blueprint as graphiql
)
from .frontend import blueprint as frontend
from .model import db
from .cli import cli

toolbar = DebugToolbarExtension()

def create_app(config_filename=None):
    app = Flask(__name__)

    app.config.from_object('bitsbox.config.default')
    if config_filename is not None:
        app.config.from_pyfile(config_filename)

    db.init_app(app)

    app.register_blueprint(ui)
    app.register_blueprint(frontend, url_prefix='/fe')
    app.register_blueprint(graphql, url_prefix='/graphql')
    app.cli.add_command(cli)

    # Things which should only be present in DEBUG-enabled apps
    if app.debug:
        app.register_blueprint(graphiql, url_prefix='/graphiql')
        toolbar.init_app(app)

    return app
