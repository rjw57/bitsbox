import unittest
from flask_fixtures import FixturesMixin

from .app import create_app
from .model import (
    db,
    Layout, LayoutItem, Cabinet, Location, Drawer
)

class TestCase(unittest.TestCase):
    db = db

    @classmethod
    def setUpClass(cls):
        app = create_app()
        app.config.from_object('bitsbox.config.testing')
        with app.app_context():
            db.create_all()
        cls.app = app

class LayoutTests(TestCase, FixturesMixin):
    fixtures = ['layouts.yaml']

    def test_layouts_are_present(self):
        assert Layout.query.count() > 0

    def test_add_layout_items(self):
        l = Layout.query.filter_by(name='44 drawer').one()
        assert l is not None
        assert LayoutItem.query.filter_by(layout=l).count() == 0
        l.add_layout_items(db.session)
        assert LayoutItem.query.filter_by(layout=l).count() == 44

        l = Layout.query.filter_by(name='64 drawer').one()
        assert l is not None
        assert LayoutItem.query.filter_by(layout=l).count() == 0
        l.add_layout_items(db.session)
        assert LayoutItem.query.filter_by(layout=l).count() == 64

class CabinetTests(TestCase, FixturesMixin):
    fixtures = ['layouts.yaml', 'cabinets.yaml']

    def setUp(self):
        for l in Layout.query.all():
            l.add_layout_items(db.session)

    def test_cabinets_are_present(self):
        assert Cabinet.query.count() > 0

    def test_linked_to_layout(self):
        c = Cabinet.query.get(1)
        assert c is not None
        assert c.layout is not None
        self.assertEqual(c.layout.name, '44 drawer')

    def test_add_locations(self):
        c = Cabinet.query.get(1)
        self.assertEqual(Location.query.filter_by(cabinet=c).count(), 0)
        c.add_locations(db.session)
        self.assertEqual(Location.query.filter_by(cabinet=c).count(), 44)

    def test_create_from_layout(self):
        l = Layout.query.filter(Layout.name=='44 drawer').one()
        assert l is not None

        n_items = LayoutItem.query.filter(LayoutItem.layout==l).count()
        self.assertGreater(n_items, 0)

        c = Cabinet.create_from_layout(db.session, l, 'Testing')
        self.assertEqual(
            n_items,
            Drawer.query.join(Drawer.location).filter(Location.cabinet==c).count()
        )

class DrawerTests(TestCase, FixturesMixin):
    fixtures = ['layouts.yaml', 'cabinets.yaml']

    def setUp(self):
        for l in Layout.query.all():
            l.add_layout_items(db.session)
        for c in Cabinet.query.all():
            c.add_locations(db.session)

    def test_create_for_cabinet_locations(self):
        c = Cabinet.query.get(1)
        self.assertEqual(len(c.locations), 44)
        self.assertEqual(
            Drawer.query.join(Drawer.location).filter(Location.cabinet==c).count(),
            0)
        Drawer.create_for_cabinet_locations(db.session, c)
        self.assertEqual(
            Drawer.query.join(Drawer.location).filter(Location.cabinet==c).count(),
            44)

if __name__ == '__main__':
    unittest.main()
