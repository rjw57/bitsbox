import sqlite3
from flask import Blueprint, current_app, g

model = Blueprint('model', __name__)

def connect_db():
    """Connects to the application database."""
    rv = sqlite3.connect(current_app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()

        @current_app.teardown_appcontext
        def close_db(_):
            """Closes the database again at the end of the request."""
            if hasattr(g, 'sqlite_db'):
                g.sqlite_db.close()
    return g.sqlite_db

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
