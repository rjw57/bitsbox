import collections
import json

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()

# The Layout model stores the specification as a JSON-encoded document. This
# type decorator is lifted from the SQLAlchemy specs but is modified to use a
# Unicode to store the value.
class JSONEncodedDict(db.TypeDecorator):
    impl = db.Unicode

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

class Layout(db.Model):
    __tablename__ = 'layouts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    spec = db.Column(JSONEncodedDict)

    cabinets = relationship('Cabinet', back_populates='layout')
    items = relationship('LayoutItem', back_populates='layout')

    def add_layout_items(self, session):
        # Walk the spec and create values for each item for a layout_items row.
        def walk_spec(spec):
            queue = collections.deque([([], spec)]) # sequence of path/spec pairs
            while len(queue) > 0:
                path, item = queue.popleft()
                type_ = item.get('type')
                if type_ == 'container':
                    queue.extend([
                        (path + [idx], c)
                        for idx, c in enumerate(item.get('children', []))])
                elif type_ == 'item':
                    yield json.dumps(path)
                else:
                    raise RuntimeError(
                        'Unknown spec type: {}'.format(repr(type_)))

        for path in walk_spec(self.spec):
            session.add(LayoutItem(spec_item_path=path, layout=self))

class Cabinet(db.Model):
    __tablename__ = 'cabinets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    layout_id = db.Column(db.Integer, db.ForeignKey('layouts.id'))

    layout = relationship('Layout', back_populates='cabinets')
    locations = relationship('Location', back_populates='cabinet')

    drawers = relationship('Drawer',
        secondary='join(Location, Drawer)', back_populates='cabinet')

    def add_locations(self, session):
        for item in LayoutItem.query.filter_by(layout=self.layout):
            session.add(Location(cabinet=self, layout_item=item))

    @classmethod
    def create_from_layout(cls, session, layout, name=None):
        """Convenience function to create a cabinet, create locations from the
        layout and to put a drawer in each location.

        """
        c = Cabinet(name=name, layout=layout)
        c.add_locations(session)
        Drawer.create_for_cabinet_locations(session, c)
        session.add(c)
        return c

class LayoutItem(db.Model):
    __tablename__ = 'layout_items'

    id = db.Column(db.Integer, primary_key=True)
    spec_item_path = db.Column(JSONEncodedDict)
    layout_id = db.Column(db.Integer, db.ForeignKey('layouts.id'))

    layout = relationship('Layout', back_populates='items')

    db.UniqueConstraint('layout_id', 'spec_item_path')

class Location(db.Model):
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True)
    cabinet_id = db.Column(db.Integer, db.ForeignKey('cabinets.id'))
    layout_item_id = db.Column(db.Integer, db.ForeignKey('layout_items.id'))

    cabinet = relationship('Cabinet', back_populates='locations')
    layout_item = relationship('LayoutItem')
    drawer = relationship('Drawer', back_populates='location', uselist=False)

class Drawer(db.Model):
    __tablename__ = 'drawers'

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.Unicode)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))

    location = relationship('Location', back_populates='drawer')
    collections = relationship('Collection', back_populates='drawer')

    cabinet = relationship('Cabinet',
        secondary='join(Location, Cabinet)', uselist=False,
        back_populates='drawers')

    @classmethod
    def create_for_cabinet_locations(cls, session, cabinet):
        locations = Location.query.filter_by(cabinet=cabinet).\
            join(Location.layout_item).order_by(LayoutItem.spec_item_path)
        for idx, l in enumerate(locations):
            session.add(Drawer(label=str(idx), location=l))

class Collection(db.Model):
    __tablename__ = 'collections'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    description = db.Column(db.Unicode)
    content_count = db.Column(db.Integer)
    drawer_id = db.Column(db.Integer, db.ForeignKey('drawers.id'))

    drawer = relationship('Drawer', back_populates='collections')
