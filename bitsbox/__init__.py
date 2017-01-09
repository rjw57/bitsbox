from flask import Flask

def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_pyfile(config_filename)

    from .ui import ui
    from .model import model
    app.register_blueprint(ui)
    app.register_blueprint(model)

    @app.cli.command('initdb')
    def initdb_command():
        """Initialises the database with the schema."""
        from .model import init_db
        init_db()

    return app
