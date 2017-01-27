from flask import Flask

from .ui import blueprint as ui
from .graphql import (
    graphql_blueprint as graphql,
    graphiql_blueprint as graphiql
)
from .model import db, migrate
from .cli import cli

def create_app(config_filename=None):
    app = Flask(__name__)

    app.config.from_object('bitsbox.config.default')
    if config_filename is not None:
        app.config.from_pyfile(config_filename)

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)

    app.register_blueprint(ui)
    app.cli.add_command(cli)

    # Things which should only be present in DEBUG-enabled apps
    if app.debug:
        from flask_debugtoolbar import DebugToolbarExtension
        toolbar = DebugToolbarExtension()
        toolbar.init_app(app)

    # GraphQL support
    app.register_blueprint(graphql, url_prefix='/graphql')
    app.register_blueprint(graphiql, url_prefix='/graphiql')

    return app
