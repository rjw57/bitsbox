import json
from flask import (
    Blueprint, render_template, abort, request, redirect, url_for, flash
)
from sqlalchemy.orm import joinedload

from .model import db, Collection, Cabinet

blueprint = Blueprint('ui', __name__)

@blueprint.route('/')
def index():
    return redirect(url_for('ui.collections'))

@blueprint.route('/collections')
def collections():
    context = {
        'collections': Collection.query.order_by(Collection.name),
    }
    return render_template('collections.html', **context)

@blueprint.route('/collections/new', methods=['GET', 'POST'])
def collection_create():
    if request.method == 'GET':
        return render_template('collection_create.html')

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
        'cabinets': Cabinet.query.options(joinedload(Cabinet.layout)),
#        'drawers_by_path': dict(
#            (row[0], row) for row in db.execute('''
#                SELECT
#                    (
#                        SELECT
#                            locations.cabinet_id || '.' || group_concat(value, '.')
#                        FROM
#                            json_each(layout_items.spec_item_path)
#                    ) AS path,
#                    drawers.id AS id,
#                    drawers.label AS label,
#                    IFNULL(
#                        (
#                            SELECT SUM(collections.content_count)
#                            FROM collections
#                            WHERE collections.drawer_id = drawers.id
#                        ),
#                        0
#                    ) AS content_count,
#                    (
#                        SELECT COUNT(1)
#                        FROM collections
#                        WHERE collections.drawer_id = drawers.id
#                    ) AS collections_count
#                FROM
#                    drawers
#                JOIN
#                    locations ON drawers.location_id = locations.id
#                JOIN
#                    layout_items ON locations.layout_item_id = layout_items.id
#                WHERE
#                    drawers.location_id IS NOT NULL
#            ''')
#        ),
    }

    return render_template('cabinets.html', **context)

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

