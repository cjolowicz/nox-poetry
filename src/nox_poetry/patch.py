"""Monkey-patch nox.sessions.Session.install with nox_poetry.install."""
from nox_poetry.core import patch


patch()
