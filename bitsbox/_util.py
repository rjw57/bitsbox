"""Utility functions."""

import base64
import os

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
