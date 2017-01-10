import json

from flask import Blueprint, render_template

from .model import get_db

blueprint = Blueprint('ui', __name__)

@blueprint.route('/')
def index():
    db = get_db()
    cabinets = db.execute(
        'SELECT id, name, layout FROM cabinets ORDER BY name, id')
    drawers = dict((row['key'], row) for row in db.execute('''
        SELECT id, cabinet_id || "." || location AS key, label
        FROM drawers
    '''))
    return render_template(
        'cabinets.html', cabinets=cabinets, drawers=drawers)

@blueprint.app_template_filter('fromjson')
def fromjson_filter(s):
    return json.loads(s)
