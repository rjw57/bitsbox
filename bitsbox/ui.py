import csv
from io import StringIO, TextIOWrapper
import json

from flask import (
    Blueprint, render_template, abort, request, redirect, url_for, flash,
    Response
)
from flask_login import login_required, logout_user
from sqlalchemy.orm import joinedload

from .model import db, Collection, Cabinet, Drawer, Layout, ResourceLink, Tag
from .user import login_manager

blueprint = Blueprint('ui', __name__, template_folder='templates/ui')

@blueprint.route('/login')
def login():
    return render_template('login.html',
        next=request.values.get('next'))

@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('ui.index'))

@blueprint.route('/')
def index():
    return redirect(url_for('ui.collections'))

@blueprint.route('/export')
@login_required
def export():
    return render_template('export.html')

@blueprint.route('/export/collections.csv')
@login_required
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

@blueprint.route('/export/resource_links.csv')
@login_required
def export_links():
    out = StringIO()
    w = csv.writer(out)

    w.writerow(['collection', 'name', 'url'])
    q = ResourceLink.query.\
        options(
            joinedload(ResourceLink.collection)
        ).\
        order_by(ResourceLink.name)
    w.writerows([
        [link.collection.name, link.name, link.url]
        for link in q
    ])

    return Response(out.getvalue(), mimetype='text/csv')

@blueprint.route('/import', endpoint='import')
@login_required
def import_index():
    context = {
        'cabinets': Cabinet.query.order_by(Cabinet.name).all(),
    }
    return render_template('import.html', **context)

@blueprint.route('/import/collections', methods=['POST'])
@login_required
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

    return redirect(url_for('ui.import'))

@blueprint.route('/import/links', methods=['POST'])
@login_required
def import_links():
    fobj = request.files.get('csv')
    if fobj is None:
        abort(400)
    fobj = TextIOWrapper(fobj)

    header = [h.lower() for h in next(csv.reader(fobj))]
    reader = csv.DictReader(fobj, fieldnames=header)

    n_added, n_updated = 0, 0
    for row in reader:
        collection_name, name, url = [
            row.get(k) for k in 'collection name url'.split()]

        # Try to get a collection for this link
        collection = Collection.query.filter(
            Collection.name==collection_name).first()

        # Skip unknown collections
        if collection is None:
            continue

        # Is there a resource link already?
        link = ResourceLink.query.filter(
            ResourceLink.collection==collection,
            ResourceLink.name==name).first()

        if link is not None:
            # Yes, update URL if necessary
            link.url = url
            n_updated += 1
        else:
            # No existing link, create one
            link = ResourceLink(
                name=name, url=url, collection=collection)
            db.session.add(link)
            n_added += 1

    db.session.commit()

    m = 'Imported {} new {}'.format(
        n_added, 'link' if n_added == 1 else 'links')
    if n_updated > 0:
        m += ' and updated {}'.format(n_updated)
    m += '.'

    flash(m)

    return redirect(url_for('ui.import'))

@blueprint.route('/collections')
@login_required
def collections():
    context = {
        'collections': Collection.query.\
            options(
                joinedload(Collection.resource_links),
                joinedload(Collection.drawer).joinedload(Drawer.cabinet),
                joinedload(Collection.tags),
            ).\
            order_by(Collection.name).all(),
    }
    return render_template('collections.html', **context)

@blueprint.route('/collections/<int:id>', methods=['GET', 'POST'])
@login_required
def collection(id):
    if request.method == 'GET':
        collection = Collection.query.options(
            joinedload(Collection.drawer).joinedload(Drawer.cabinet),
            joinedload(Collection.resource_links),
            joinedload(Collection.tags)
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
            'tag_data': { 'tags': [t.name for t in Tag.query_used()] },
        }

        return render_template('collection.html', **context)

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

    tag_objects = []
    for tag_name in request.values.getlist('tags'):
        tag = Tag.query.filter(Tag.name==tag_name).first()
        if tag is None:
            tag = Tag(name=tag_name)
            db.session.add(tag)
        tag_objects.append(tag)

    Collection.query.filter(Collection.id==collection.id).update({
        Collection.name: name, Collection.description: description,
        Collection.content_count: count,
        Collection.drawer_id: drawer_id
    })

    Collection.query.get(collection.id).tags = tag_objects

    db.session.commit()

    flash('Collection "{}" updated.'.format(name))

    return redirect(url_for('ui.collection', id=collection.id))

@blueprint.route('/collections/<int:id>/delete', methods=['POST'])
@login_required
def collection_delete(id):
    collection = Collection.query.get(id)
    if collection is None:
        abort(404)

    Collection.query.filter(Collection.id == id).delete()
    db.session.commit()

    flash('Collection "{}" deleted'.format(collection.name))

    return redirect(url_for('ui.collections'))

@blueprint.route('/collections/new', methods=['GET', 'POST'])
@login_required
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
@login_required
def cabinets():
    context = {
        'cabinets': Cabinet.query.options(
            joinedload(Cabinet.drawers),
            joinedload(Cabinet.layout),
        ).order_by(Cabinet.name).all(),
        'layouts': Layout.query.all(),
    }

    return render_template('cabinets.html', **context)

@blueprint.route('/cabinet/<int:id>', methods=['GET', 'POST'])
@login_required
def cabinet(id):
    if request.method == 'GET':
        cabinet = Cabinet.query.get(id)
        if cabinet is None:
            abort(404)

        context = {
            'cabinet': cabinet,
            'layouts': Layout.query.all(),
        }

        return render_template('cabinet.html', **context)

    cabinet = Cabinet.query.get(id)
    if cabinet is None:
        abort(404)

    name = request.values.get('name', '')
    if name == '':
        abort(400)

    cabinet.name = name
    db.session.commit()

    flash('Cabinet "{}" updated.'.format(cabinet.name))

    return redirect(url_for('ui.cabinet', id=cabinet.id))

@blueprint.route('/cabinet/<int:id>/delete', methods=['POST'])
@login_required
def cabinet_delete(id):
    cabinet = Cabinet.query.get(id)
    if cabinet is None:
        abort(404)

    Cabinet.query.filter(Cabinet.id == id).delete()
    db.session.commit()

    flash('Cabinet "{}" deleted'.format(cabinet.name))

    return redirect(url_for('ui.cabinets'))

@blueprint.route('/cabinets/new', methods=['GET', 'POST'])
@login_required
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

@blueprint.route('/links/new', methods=['POST'])
@login_required
def link_create():
    collection = Collection.query.filter(
        Collection.id==int(request.values.get('collection_id'))).first()
    if collection is None:
        abort(400)

    name, url = [request.values.get(k, '') for k in 'name url'.split()]
    if name == '' or url == '':
        abort(400)

    link = ResourceLink(name=name, url=url, collection=collection)
    db.session.add(link)
    db.session.commit()

    flash('Link "{}" added'.format(name))

    return redirect(url_for('ui.collection', id=collection.id))

@blueprint.route('/link/<int:id>/delete', methods=['POST'])
@login_required
def link_delete(id):
    link = ResourceLink.query.options(
        joinedload(ResourceLink.collection)).filter(ResourceLink.id==id).first()
    if not link:
        abort(404)

    ResourceLink.query.filter(ResourceLink.id==id).delete()
    db.session.commit()

    flash('Link "{}" deleted.'.format(link.name))

    return redirect(url_for('ui.collection', id=link.collection.id))
