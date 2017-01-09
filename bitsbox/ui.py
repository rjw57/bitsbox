from flask import Blueprint, render_template
import yaml

ui = Blueprint('ui', __name__)

with open('containers.yaml') as f:
    COLLECTIONS = yaml.load(f)['collections']

@ui.route('/')
def index():
    return render_template('containers.html', collections=COLLECTIONS)
