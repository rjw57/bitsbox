import json

from flask import (
    Blueprint, render_template, abort, request, redirect, url_for, flash
)

from .db import get_db

blueprint = Blueprint('ui', __name__)

@blueprint.route('/')
def index():
    return redirect(url_for('ui.collections'))

@blueprint.route('/collections')
def collections():
    db = get_db()
    context = {
        'collections': db.execute('''
            SELECT
                collections.id AS collection_id, collections.name AS name,
                collections.description AS description,
                collections.contents_count AS contents_count,
                drawers.id AS drawer_id, drawers.label AS drawer_label,
                cabinets.id AS cabinet_id, cabinets.name AS cabinet_name
            FROM
                collections
            LEFT OUTER JOIN
                drawers ON drawers.id = collections.drawer_id
            LEFT OUTER JOIN
                locations ON drawers.location_id = locations.id
            LEFT OUTER JOIN
                cabinets ON locations.cabinet_id = cabinets.id
            ORDER BY
                name, collection_id
        '''),
    }
    return render_template('collections.html', **context)

@blueprint.route('/collections/new', methods=['GET', 'POST'])
def collection_create():
    if request.method == 'GET':
        return render_template('collection_create.html')

    db = get_db()

    # This is the POST request, extract the form values
    name = request.values.get('name', '')
    if name == '':
        abort(400)

    description = request.values.get('description', '')
    if description == '':
        abort(400)

    contents_count = int(request.values.get('count', 0))

    # Create the collection
    db.execute('''
        INSERT INTO
            collections (name, description, contents_count)
        VALUES
            (?, ?, ?)
    ''', (name, description, contents_count))
    db.commit()

    flash('Collection "{}" created'.format(name))

    return redirect(url_for('ui.collections'))

@blueprint.route('/cabinets')
def cabinets():
    db = get_db()

    context = {
        'cabinets': db.execute('''
            SELECT
                cabinets.id AS id,
                cabinets.name AS name,
                layouts.spec AS layout
            FROM
                cabinets JOIN layouts
            ON
                cabinets.layout_id = layouts.id
            ORDER BY
                cabinets.name
        '''),
        'drawers_by_path': dict(
            (row[0], row) for row in db.execute('''
                SELECT
                    (
                        SELECT
                            locations.cabinet_id || '.' || group_concat(value, '.')
                        FROM
                            json_each(layout_items.spec_item_path)
                    ) AS path,
                    drawers.id AS id,
                    drawers.label AS label,
                    IFNULL(
                        (
                            SELECT SUM(collections.contents_count)
                            FROM collections
                            WHERE collections.drawer_id = drawers.id
                        ),
                        0
                    ) AS contents_count,
                    (
                        SELECT COUNT(1)
                        FROM collections
                        WHERE collections.drawer_id = drawers.id
                    ) AS collections_count
                FROM
                    drawers
                JOIN
                    locations ON drawers.location_id = locations.id
                JOIN
                    layout_items ON locations.layout_item_id = layout_items.id
                WHERE
                    drawers.location_id IS NOT NULL
            ''')
        ),
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
                contents_count
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


@blueprint.app_template_filter('fromjson')
def fromjson_filter(s):
    return json.loads(s)
