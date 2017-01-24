import csv
from io import StringIO, TextIOWrapper
import json

from flask import (
    Blueprint, render_template, abort, request, redirect, url_for, flash,
    Response
)
from sqlalchemy.orm import joinedload

from .model import db, Collection, Cabinet, Drawer, Layout
from .graphql import schema

blueprint = Blueprint('ui', __name__)

@blueprint.route('/')
def index():
    return redirect(url_for('ui.collections'))

@blueprint.route('/export')
def export():
    return render_template('export.html')

@blueprint.route('/export/collections.csv')
def export_collections():
    out = StringIO()
    w = csv.writer(out)

    w.writerow(['name', 'description', 'count', 'cabinet', 'drawer'])
    q = Collection.query.\
        options(
            joinedload(Collection.drawer).
            joinedload(Drawer.cabinet)
        ).\
        order_by(Collection.name)
    w.writerows([
        [
            collection.name, collection.description,
            collection.content_count,
            collection.drawer.cabinet.name if collection.drawer is not None else '',
            collection.drawer.label if collection.drawer is not None else ''
        ]
        for collection in q
    ])

    return Response(out.getvalue(), mimetype='text/csv')

@blueprint.route('/collections/import', methods=['POST'])
def import_collections():
    fobj = request.files.get('csv')
    if fobj is None:
        abort(400)
    fobj = TextIOWrapper(fobj)

    header = [h.lower() for h in next(csv.reader(fobj))]
    reader = csv.DictReader(fobj, fieldnames=header)

    n_added, n_skipped = 0, 0
    for row in reader:
        if row.get('name', '') == '':
            continue

        if Collection.query.filter(Collection.name==row.get('name')).count() > 0:
            n_skipped += 1
            continue

        drawer = Drawer.query.filter(
            Cabinet.name==row.get('cabinet'),
            Drawer.label==row.get('drawer')).first()
        if drawer is None:
            continue

        db.session.add(Collection(name=row.get('name'),
            description=row.get('description'),
            content_count=int(row.get('count', 1)),
            drawer=drawer))
        n_added += 1

    db.session.commit()

    m = 'Imported {} {}.'.format(
        n_added, 'collection' if n_added == 1 else 'collections')
    if n_skipped > 0:
        m += ' Skipped {} {}.'.format(
            n_skipped, 'duplicate' if n_skipped == 1 else 'duplicates')

    flash(m)

    return redirect(url_for('ui.collections'))

@blueprint.route('/collections')
def collections():
    context = {
        'collections': Collection.query.\
            options(
                joinedload(Collection.drawer).
                joinedload(Drawer.cabinet)
            ).\
            order_by(Collection.name),
    }
    return render_template('collections.html', **context)

@blueprint.route('/collections/<int:id>')
def collection(id):
    collection = Collection.query.options(
        joinedload(Collection.drawer).joinedload(Drawer.cabinet)
    ).get(id)
    if collection is None:
        abort(404)

    cabinets = Cabinet.query.options(joinedload(Cabinet.drawers)).all()
    context = {
        'cabinets': cabinets,
        'drawers': {
            'byCabinetId': dict(
                (str(c.id), [
                    {'id':str(d.id), 'label':d.label} for d in c.drawers
                ])
                for c in cabinets
            ),
        },
        'collection': collection,
    }

    return render_template('collection.html', **context)

@blueprint.route('/collections/new', methods=['GET', 'POST'])
def collection_create():
    if request.method == 'GET':
        cabinets = Cabinet.query.options(joinedload(Cabinet.drawers)).all()
        context = {
            'cabinets': cabinets,
            'drawers': {
                'byCabinetId': dict(
                    (str(c.id), [
                        {'id':str(d.id), 'label':d.label} for d in c.drawers
                    ])
                    for c in cabinets
                ),
            },
        }
        return render_template('collection_create.html', **context)

    # This is the POST request, extract the form values
    name = request.values.get('name', '')
    if name == '':
        abort(400)

    description = request.values.get('description', '')
    if description == '':
        abort(400)

    content_count = int(request.values.get('count', 0))

    # Create the collection
    collection = Collection(
        name=name, description=description, content_count=content_count)
    db.session.add(collection)
    db.session.commit()

    flash('Collection "{}" created'.format(name))

    return redirect(url_for('ui.collections'))

@blueprint.route('/cabinets')
def cabinets():
    context = {
        'cabinets': Cabinet.query.options(
            joinedload(Cabinet.drawers),
            joinedload(Cabinet.layout),
        ).all(),
        'layouts': Layout.query.all(),
    }

    return render_template('cabinets.html', **context)

@blueprint.route('/cabinets/new', methods=['GET', 'POST'])
def cabinet_create():
    if request.method == 'GET':
        context = {
            'layouts': Layout.query.all(),
        }
        return render_template('cabinet_create.html', **context)

    layout = Layout.query.get(int(request.values.get('layout')))
    if layout is None:
        abort(400)

    name = request.values.get('name', '')
    if name == '':
        abort(400)

    Cabinet.create_from_layout(db.session, layout, name,
        drawer_prefix=request.values.get('prefix', ''))
    db.session.commit()
    flash('Cabinet "{}" created'.format(name))

    return redirect(url_for('ui.cabinets'))

@blueprint.route('/drawer/<int:drawer_id>')
def drawer(drawer_id):
    db = get_db()

    context = {
        'drawer': db.execute('''
            SELECT
                drawers.id AS id,
                drawers.label AS label
            FROM
                drawers
            WHERE
                drawers.id = ?
        ''', (drawer_id,)).fetchone(),
        'location': db.execute('''
            SELECT
                cabinets.id AS cabinet_id,
                locations.id AS location_id,
                cabinets.name AS cabinet_name,
                layout_items.spec_item_path AS spec_item_path
            FROM
                drawers
            JOIN
                locations ON drawers.location_id = locations.id
            JOIN
                layout_items ON locations.layout_item_id = layout_items.id
            JOIN
                cabinets ON locations.cabinet_id = cabinets.id
            WHERE
                drawers.id = ?
        ''', (drawer_id,)).fetchone(),
        'collections': db.execute('''
            SELECT
                id AS collection_id,
                name,
                description,
                content_count
            FROM
                collections
            WHERE
                drawer_id = ?
            ORDER BY
                name, id
        ''', (drawer_id,)).fetchall(),
    }

    if context['drawer'] is None:
        abort(404)

    return render_template('drawer.html', **context)

