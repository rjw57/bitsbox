from flask import Blueprint, render_template

blueprint = Blueprint(
    'frontend', __name__, static_folder='frontend/static',
    template_folder='frontend/templates')

@blueprint.route('/')
def index():
    return render_template('index.html')
