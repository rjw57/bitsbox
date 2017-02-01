"""Utility functions."""
import base64
import os
from urllib.parse import urlparse, urljoin

from flask import request

_DEFAULT_NBYTES=32

def _token_bytes(nbytes=None):
    return os.urandom(nbytes if nbytes is not None else _DEFAULT_NBYTES)

def _token_urlsafe(nbytes=None):
    """Generate a random URL-safe string containing nbytes of entropy."""
    return base64.urlsafe_b64encode(
        _token_bytes(nbytes)).rstrip(b'=').decode('ascii')

# Use the secrets module implementation in preference.
try:
    from secrets import token_urlsafe
except ImportError:
    token_urlsafe = _token_urlsafe

# See http://flask.pocoo.org/snippets/62/
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc
