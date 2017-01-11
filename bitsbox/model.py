from collections import deque
import copy
import json
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
import yaml

from ._util import token_urlsafe

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

def create_cabinet(cursor, name, layout_id):
    """Creates a new cabinet with the specified name and layout id.
    Automatically creates one drawer for each item of the layout spec.

    Returns: rowid of newly created cabinet.

    """
    cursor.execute(
        'INSERT INTO cabinets (name, layout_id) VALUES (?, ?)',
        (name, layout_id))
    cabinet_id = cursor.lastrowid
    assert cabinet_id is not None and cabinet_id > 0

    # Create a new location for each item in the layout spec
    cursor.execute('''
        INSERT INTO
            locations (cabinet_id, layout_item_id)
        SELECT
            cabinets.id, layout_items.id
        FROM
            cabinets JOIN layout_items
        ON
            cabinets.layout_id = layout_items.layout_id
        WHERE
            cabinets.id = ?
    ''', (cabinet_id,))

    # Create a new drawer for each location
    cursor.execute('''
        INSERT INTO
            drawers (label, location_id)
        SELECT
            (
                SELECT
                    group_concat(value, '.')
                FROM
                    json_each(layout_items.spec_item_path)
            ),
            locations.id
        FROM
            locations JOIN layout_items
        ON
            locations.layout_item_id = layout_items.id
        WHERE
            locations.cabinet_id = ?
    ''', (cabinet_id,))


    return cabinet_id

@cli.command('initdb')
@with_appcontext
def initdb_command():
    """Initialises the database with the schema."""
    init_db()

@cli.command('addcabinet')
@click.argument('name', type=str)
@click.argument('layout_id', type=int)
@with_appcontext
def addcabinet_command(name, layout_id):
    db = get_db()
    cabinet_id = create_cabinet(db.cursor(), name, layout_id)
    db.commit()
    print('Created cabinet "{}" with id: {}'.format(name, cabinet_id))

@cli.command('importlayouts')
@click.argument('yaml_file', type=click.File('rb'))
@with_appcontext
def importcabs_command(yaml_file):
    db = get_db()
    cur = db.cursor()

    for layout in yaml.load(yaml_file).get('layouts', []):
        name, spec = [layout[k] for k in 'name spec'.split()]
        existing_layout_id = cur.execute('''
            SELECT 1 FROM layouts WHERE name = ? LIMIT 1
        ''', (name,))
        if existing_layout_id.fetchone() is not None:
            print('Skipping existing layout: {}'.format(name))
            continue

        # Insert layout into DB
        cur.execute(
            'INSERT INTO layouts (name, spec) VALUES (?, ?)',
            (name, json.dumps(spec)))
        layout_id = cur.lastrowid
        assert layout_id is not None and layout_id > 0

        # Walk the spec and create values for each item for a layout_items row.
        def walk_spec(spec, layout_id):
            queue = deque([([], spec)]) # sequence of path/spec pairs
            while len(queue) > 0:
                path, item = queue.popleft()
                type_ = item.get('type')
                if type_ == 'container':
                    queue.extend([
                        (path + [idx], c)
                        for idx, c in enumerate(item.get('children', []))])
                elif type_ == 'item':
                    yield json.dumps(path), layout_id
                else:
                    raise RuntimeError(
                        'Unknown spec type: {}'.format(repr(type_)))

        cur.executemany(
            'INSERT INTO layout_items (spec_item_path, layout_id) VALUES (?, ?)',
            walk_spec(spec, layout_id))

        print('Importing layout "{}" with id: {}'.format(name, layout_id))

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
