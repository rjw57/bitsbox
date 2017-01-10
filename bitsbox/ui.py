import json

from flask import Blueprint, render_template

from .model import get_db

blueprint = Blueprint('ui', __name__)

@blueprint.route('/')
def index():
    db = get_db()
    cabinets = db.execute(
        'SELECT name, layout AS "layout [json]" FROM cabinets')
    return render_template('cabinets.html', cabinets=cabinets)

@blueprint.app_template_filter('fromjson')
def fromjson_filter(s):
    return json.loads(s)
