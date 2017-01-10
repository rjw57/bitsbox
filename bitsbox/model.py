import json
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
import yaml

def connect_db():
    """Connects to the application database."""
    rv = sqlite3.connect(current_app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def close_db(_):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
        delattr(g, 'sqlite_db')

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()

    return g.sqlite_db

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

cli = click.Group('model', help='Manipulates the database.')

@cli.command('initdb')
@with_appcontext
def initdb_command():
    """Initialises the database with the schema."""
    init_db()

@cli.command('importcabs')
@click.argument('yaml_file', type=click.File('rb'))
@with_appcontext
def importcabs_command(yaml_file):
    db = get_db()
    cur = db.cursor()

    cabinets = yaml.load(yaml_file).get('cabinets')
    if cabinets is None:
        raise RuntimeError('Input file has no "cabinets" key')

    for cabinet in cabinets:
        name, layout = [cabinet[k] for k in 'name layout'.split()]
        cur.execute(
            'INSERT INTO cabinets (name, layout) VALUES (?, ?)',
            (name, json.dumps(layout)))
        cabinet_id = cur.lastrowid

        print('Importing cabinet {} ({})'.format(cabinet_id, name))
        cur.executemany(
            'INSERT INTO drawers (label, cabinet_id, location) VALUES (?, ?, ?)',
            [
                ('{} {}'.format(name, loc), cabinet_id, loc)
                for loc in layout_drawer_locations(layout)
            ])

    db.commit()

def layout_drawer_locations(layout, path=None):
    path = path or []
    type_ = layout.get('type')
    if type_ == 'drawer':
        yield '.'.join(path)
    elif type_ == 'container':
        for idx, item in enumerate(layout.get('items', [])):
            for rv in layout_drawer_locations(item, path=path + [str(idx)]):
                yield rv
    else:
        raise RuntimeError('Unknown layout type: {}'.format(repr(type_)))
