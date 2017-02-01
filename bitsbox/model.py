import collections
import json
from sqlite3 import Connection as SQLite3Connection

from flask_login import UserMixin
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event as sqlalchemy_event, MetaData
from sqlalchemy.engine import Engine
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import DEFAULT_NAMING_CONVENTION
from sqlalchemy_utils.types.url import URLType

# Ensure that sqlite honours foreign key constraints
# http://stackoverflow.com/questions/2614984/a
@sqlalchemy_event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

db = SQLAlchemy(
    metadata=MetaData(naming_convention=DEFAULT_NAMING_CONVENTION)
)
migrate = Migrate()

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
    name = db.Column(db.Unicode, unique=True, nullable=False)
    spec = db.Column(JSONEncodedDict, nullable=False)

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
    name = db.Column(db.Unicode, unique=True, nullable=False)
    layout_id = db.Column(db.Integer,
        db.ForeignKey('layouts.id', ondelete='CASCADE'),
        nullable=False)

    layout = relationship('Layout', back_populates='cabinets')
    locations = relationship('Location', back_populates='cabinet')

    drawers = relationship('Drawer',
        secondary='join(Location, Drawer)', back_populates='cabinet')

    def add_locations(self, session):
        for item in LayoutItem.query.filter_by(layout=self.layout):
            session.add(Location(cabinet=self, layout_item=item))

    @classmethod
    def create_from_layout(cls, session, layout, name=None, drawer_prefix=None):
        """Convenience function to create a cabinet, create locations from the
        layout and to put a drawer in each location.

        """
        c = Cabinet(name=name, layout=layout)
        c.add_locations(session)
        Drawer.create_for_cabinet_locations(session, c, prefix=drawer_prefix)
        session.add(c)
        return c

class LayoutItem(db.Model):
    __tablename__ = 'layout_items'

    id = db.Column(db.Integer, primary_key=True)
    spec_item_path = db.Column(JSONEncodedDict, nullable=False)
    layout_id = db.Column(db.Integer,
        db.ForeignKey('layouts.id', ondelete='CASCADE'),
        nullable=False)

    layout = relationship('Layout', back_populates='items')

    db.UniqueConstraint('layout_id', 'spec_item_path')

class Location(db.Model):
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True)
    cabinet_id = db.Column(db.Integer,
        db.ForeignKey('cabinets.id', ondelete='CASCADE'),
        nullable=False)
    layout_item_id = db.Column(db.Integer,
        db.ForeignKey('layout_items.id', ondelete='CASCADE'),
        nullable=False)

    cabinet = relationship('Cabinet', back_populates='locations')
    layout_item = relationship('LayoutItem')
    drawer = relationship('Drawer', back_populates='location', uselist=False)

    db.UniqueConstraint('cabinet_id', 'layout_item_id')

class Drawer(db.Model):
    __tablename__ = 'drawers'

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.Unicode, nullable=False)
    location_id = db.Column(db.Integer,
        db.ForeignKey('locations.id', ondelete='CASCADE'),
        nullable=False)

    location = relationship('Location', back_populates='drawer')
    collections = relationship('Collection', back_populates='drawer')

    cabinet = relationship('Cabinet',
        secondary='join(Location, Cabinet)', uselist=False,
        back_populates='drawers')

    @classmethod
    def create_for_cabinet_locations(cls, session, cabinet, prefix=None):
        locations = Location.query.filter_by(cabinet=cabinet).\
            join(Location.layout_item).order_by(LayoutItem.spec_item_path)
        for idx, l in enumerate(locations):
            session.add(Drawer(
                label='{}{}'.format(prefix or '', idx + 1), location=l))

class Collection(db.Model):
    __tablename__ = 'collections'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, unique=True, nullable=False)
    description = db.Column(db.Unicode, nullable=False)
    content_count = db.Column(db.Integer)
    drawer_id = db.Column(db.Integer,
        db.ForeignKey('drawers.id', ondelete='SET NULL'))

    drawer = relationship('Drawer', back_populates='collections')
    resource_links = relationship('ResourceLink', back_populates='collection')

class ResourceLink(db.Model):
    __tablename__ = 'resource_links'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, nullable=False)
    collection_id = db.Column(db.Integer,
        db.ForeignKey('collections.id', ondelete='CASCADE'),
        nullable=False)
    url = db.Column(URLType, nullable=False)

    collection = relationship('Collection', back_populates='resource_links')

    db.UniqueConstraint('name', 'collection_id')

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    picture_url = db.Column(URLType)

class GoogleUser(db.Model):
    __tablename__ = 'google_users'

    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.Unicode, nullable=False, unique=True)
    email = db.Column(db.Unicode, nullable=False)
    email_verified = db.Column(db.Boolean, nullable=False)
    name = db.Column(db.Unicode, nullable=False)
    picture_url = db.Column(URLType, nullable=False)
    given_name = db.Column(db.Unicode, nullable=False)
    family_name = db.Column(db.Unicode, nullable=False)
    locale = db.Column(db.Unicode, nullable=False)

    user_id = db.Column(db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False)

    user = relationship('User')
