# Experimental repository

This repository contains a sketch of some ideas for a webapp. It's of little
interest to anyone else and of even littler use.

## Development server

```console
$ export BITSBOX_CONFIG=$PWD/config.py
$ export FLASK_APP=bitsbox.autoapp
$ export FLASK_DEBUG=1
$ flask db upgrade
$ flask bitsbox importlayouts layouts.yaml
$ flask run
```

The ``config.py`` file should look something like the following:

```python
from bitsbox.config.dev import *

# Set to True to allow implicit user creation. The first user created is
# implicitly the admin user.
USER_CREATION_ALLOWED=False
GOOGLE_CLIENT_ID='YOUR_CLIENT_ID.apps.googleusercontent.com'
```

Get a Google client id by creating a new project on the Google developers'
console.

