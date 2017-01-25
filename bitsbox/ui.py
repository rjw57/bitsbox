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

    n_added, n_updated = 0, 0
    for row in reader:
        name, drawer_label, cabinet, description = [
            row.get(k) for k in 'name drawer cabinet description'.split()]

        count = int(row.get('count', 1))

        if name is None or name == '':
            continue

        # Try to get a drawer for this collection
        drawer = None
        if drawer_label is not None and cabinet is not None:
            drawer = Drawer.query.filter(
                Cabinet.name==cabinet,
                Drawer.label==drawer_label).first()

        # See if there's an existing collection with this name
        collection = Collection.query.filter(
            Collection.name==row.get('name')).first()

        # If no collection, create one
        if collection is None:
            db.session.add(Collection(name=row.get('name'),
                description=description,
                content_count=count,
                drawer=drawer))
            n_added += 1
        else:
            # Otherwise, update
            Collection.query.filter(Collection.id==collection.id).update({
                Collection.description: description,
                Collection.content_count: count,
                Collection.drawer_id: drawer.id if drawer is not None else None
            })
            n_updated += 1

    db.session.commit()

    m = 'Imported {} new {}'.format(
        n_added, 'collection' if n_added == 1 else 'collections')
    if n_updated > 0:
        m += ' and updated {}'.format(n_updated)
    m += '.'

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
            order_by(Collection.name).all(),
    }
    return render_template('collections.html', **context)

@blueprint.route('/collections/<int:id>')
def collection(id):
    collection = Collection.query.options(
        joinedload(Collection.drawer).joinedload(Drawer.cabinet)
    ).get(id)
    if collection is None:
        abort(404)

    cabinets = Cabinet.query.options(joinedload(Cabinet.drawers)).\
        order_by(Cabinet.name).all()
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

@blueprint.route('/collections/<int:id>/update', methods=['POST'])
def collection_update(id):
    collection = Collection.query.get(id)
    if collection is None:
        abort(404)

    name, description = [
        request.values.get(k, '') for k in 'name description'.split()]

    if name == '' or description == '':
        abort(400)

    count = int(request.values.get('count', 1))

    drawer_id = request.values.get('drawer')
    if drawer_id is not None:
        drawer_id = int(drawer_id)
        # check this drawer exists!
        if Drawer.query.get(drawer_id) is None:
            abort(400)

    Collection.query.filter(Collection.id==collection.id).update({
        Collection.name: name, Collection.description: description,
        Collection.content_count: count,
        Collection.drawer_id: drawer_id
    })

    db.session.commit()

    flash('Collection "{}" updated.'.format(name))

    return redirect(url_for('ui.collection', id=collection.id))

@blueprint.route('/collections/new')
def collection_create():
    if request.method == 'GET':
        cabinets = Cabinet.query.options(joinedload(Cabinet.drawers)).\
            order_by(Cabinet.name).all()
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
        ).order_by(Cabinet.name).all(),
        'layouts': Layout.query.all(),
    }

    return render_template('cabinets.html', **context)

@blueprint.route('/cabinet/<int:id>')
def cabinet(id):
    cabinet = Cabinet.query.get(id)
    if cabinet is None:
        abort(404)

    context = {
        'cabinet': cabinet,
        'layouts': Layout.query.all(),
    }

    return render_template('cabinet.html', **context)

@blueprint.route('/cabinet/<int:id>/delete')
def cabinet_delete(id):
    cabinet = Cabinet.query.get(id)
    if cabinet is None:
        abort(404)

    Cabinet.query.filter(Cabinet.id == id).delete()
    db.session.commit()

    flash('Cabinet "{}" deleted'.format(cabinet.name))

    return redirect(url_for('ui.cabinets'))

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

