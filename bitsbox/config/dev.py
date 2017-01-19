from bitsbox._util import token_urlsafe

SQLALCHEMY_DATABASE_URI='sqlite:///db.sqlite'
SECRET_KEY=token_urlsafe()
