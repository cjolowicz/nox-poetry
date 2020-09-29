"""Monkey-patch Nox to install packages using nox-poetry.

Import this module to monkey-patch Nox.
See :func:`nox_poetry.core.patch` for details.
"""
from nox_poetry.core import patch


patch()
