import unittest
from flask_fixtures import FixturesMixin

from .app import create_app
from .model import (
    db,
    Layout, LayoutItem, Cabinet
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

    def test_cabinets_are_present(self):
        assert Cabinet.query.count() > 0

    def test_linked_to_layout(self):
        c = Cabinet.query.get(1)
        assert c is not None
        assert c.layout is not None
        self.assertEqual(c.layout.name, '44 drawer')

if __name__ == '__main__':
    unittest.main()
