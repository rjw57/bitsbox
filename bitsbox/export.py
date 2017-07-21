import csv

from sqlalchemy.orm import joinedload

from .model import Collection, Drawer, ResourceLink

def write_collections_csv(output_fobj):
    w = csv.writer(output_fobj)

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

def write_links_csv(output_fobj):
    w = csv.writer(output_fobj)

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

def write_tags_csv(output_fobj):
    w = csv.writer(output_fobj)

    w.writerow(['collection', 'tag'])
    q = Collection.query.options(
        joinedload(Collection.tags)).order_by(Collection.name)
    for collection in q:
        w.writerows([
            [collection.name, tag.name]
            for tag in collection.tags
        ])
