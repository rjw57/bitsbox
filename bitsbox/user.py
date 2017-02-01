from flask import current_app, Blueprint, request, redirect, url_for, abort
from flask_login import LoginManager, login_user
from oauth2client import client, crypt

from .model import User, GoogleUser, db
from ._util import is_safe_url

blueprint = Blueprint('login', __name__)

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    try:
        id = int(user_id)
    except TypeError:
        return None
    return User.query.get(user_id)

@blueprint.route('/token/google', methods=['POST'])
def google_token():
    # Parse and verify Google token as authentic
    idinfo = _parse_and_verify_token(request.values['token'])

    # Is there an existing user for this ID?
    google_user = GoogleUser.query.filter(
        GoogleUser.unique_id==idinfo['sub']).first()

    if google_user is None:
        # Cannot create user if disabled in config
        if not current_app.config.get('USER_CREATION_ALLOWED', False):
            abort(403)

        # Create a new user for this Google user
        user = User(
            name=idinfo['name'], picture_url=idinfo['picture'])
        db.session.add(user)

        # Create a new Google user with the full profile information
        google_user = GoogleUser(
            unique_id=idinfo['sub'], email=idinfo['email'],
            email_verified=idinfo['email_verified']=='true',
            name=idinfo['name'], picture_url=idinfo['picture'],
            given_name=idinfo['given_name'], family_name=idinfo['family_name'],
            locale=idinfo['locale'], user=user)
        db.session.add(google_user)
    else:
        # Update Google user fields
        google_user.email = idinfo['email']
        google_user.email_verified = idinfo['email_verified'] == 'true'
        google_user.name = idinfo['name']
        google_user.picture_url = idinfo['picture']
        google_user.given_name = idinfo['given_name']
        google_user.family_name = idinfo['family_name']
        google_user.locale = idinfo['locale']

        # Retrive user and update picture URL if not present
        user = google_user.user
        if user.picture_url is None:
            user.picture_url = idinfo['picture']

    db.session.commit()

    login_user(user)

    next_url = request.values.get('next')
    if next_url is None or not is_safe_url(next_url):
        return redirect(url_for('ui.index'))
    return redirect(next_url)

def _parse_and_verify_token(token):
    valid_issuers = ['accounts.google.com', 'https://accounts.google.com']

    idinfo = client.verify_id_token(token,
        current_app.config['GOOGLE_CLIENT_ID'])

    if idinfo['iss'] not in valid_issuers:
        raise crypt.AppIdentityError("Wrong issuer.")

    return idinfo
