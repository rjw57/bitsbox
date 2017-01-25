import os
from flask.helpers import get_root_path
from bitsbox._util import token_urlsafe

DEBUG=True
SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(
    get_root_path('bitsbox'), 'db.sqlite')
SECRET_KEY=token_urlsafe()
DEBUG_TB_INTERCEPT_REDIRECTS=False
