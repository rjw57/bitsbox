import click
from flask.cli import with_appcontext
import yaml

from .model import db, Layout, Cabinet

cli = click.Group('bitsbox', help='Commands specific to bitsbox')

@cli.command('initdb')
@with_appcontext
def initdb_command():
    """Initialises the database with the schema."""
    db.create_all()

@cli.command('importlayouts')
@click.argument('yaml_file', type=click.File('rb'))
@with_appcontext
def importlayouts_command(yaml_file):
    """Import layouts defined in a YAML file.
    """
    session = db.session

    for layout in yaml.load(yaml_file).get('layouts', []):
        name, spec = [layout[k] for k in 'name spec'.split()]

        if Layout.query.filter(Layout.name==name).count() > 0:
            print('Skipping existing layout: {}'.format(name))
            continue

        layout = Layout(name=name, spec=spec)
        layout.add_layout_items(session)
        session.add(layout)

        print('Importing layout "{}" with id: {}'.format(
            name, Layout.query.filter(Layout.name==name).one().id))

    session.commit()

@cli.command('addcabinet')
@click.argument('name', type=str)
@click.argument('layout_id', type=int)
@with_appcontext
def addcabinet_command(name, layout_id):
    """Add a cabinet with the specified layout id and create all drawers."""
    session = db.session

    if Cabinet.query.filter(Cabinet.name==name).count() > 0:
        print('Not adding cabinet with non-unique name')
        return

    layout = Layout.query.get(layout_id)
    assert layout is not None
    Cabinet.create_from_layout(session, layout, name)
    session.commit()

    print('Created cabinet "{}" with layout "{}"'.format(name, layout.name))
