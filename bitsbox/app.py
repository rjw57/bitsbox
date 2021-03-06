from flask import Flask

from .ui import blueprint as ui
from .model import db, migrate
from .cli import cli
from .user import login_manager, blueprint as login

def create_app(config_filename=None):
    app = Flask(__name__)

    app.config.from_object('bitsbox.config.default')
    if config_filename is not None:
        app.config.from_pyfile(config_filename)

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)

    login_manager.login_view = 'ui.login'
    login_manager.init_app(app)

    app.register_blueprint(ui)
    app.register_blueprint(login)
    app.cli.add_command(cli)

    # Things which should only be present in DEBUG-enabled apps
    app.debug = app.config.get('DEBUG', False)
    if app.debug:
        from flask_debugtoolbar import DebugToolbarExtension
        toolbar = DebugToolbarExtension()
        toolbar.init_app(app)

    return app
