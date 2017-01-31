from flask_login import LoginManager

from .model import User

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    try:
        id = int(user_id)
    except TypeError:
        return None
    return User.get(user_id)

