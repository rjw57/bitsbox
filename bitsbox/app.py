from flask import Flask

from .ui import blueprint as ui
from .model import db
from .cli import cli

def create_app(config_filename=None):
    app = Flask(__name__)

    app.config.from_object('bitsbox.config.default')
    if config_filename is not None:
        app.config.from_pyfile(config_filename)

    db.init_app(app)
    app.register_blueprint(ui)
    app.cli.add_command(cli)

    return app
