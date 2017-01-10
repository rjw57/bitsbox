from flask import Flask

from .ui import blueprint as ui
from .model import cli as model_cli, close_db

def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_pyfile(config_filename)

    app.teardown_appcontext(close_db)

    app.register_blueprint(ui)

    app.cli.add_command(model_cli)

    return app
