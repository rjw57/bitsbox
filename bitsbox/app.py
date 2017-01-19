from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

from .ui import blueprint as ui
from .model import db
from .cli import cli

toolbar = DebugToolbarExtension()

def create_app(config_filename=None):
    app = Flask(__name__)

    app.config.from_object('bitsbox.config.default')
    if config_filename is not None:
        app.config.from_pyfile(config_filename)

    db.init_app(app)
    toolbar.init_app(app)

    app.register_blueprint(ui)
    app.cli.add_command(cli)

    return app
