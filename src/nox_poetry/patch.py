"""Monkey-patch Nox to install packages using nox-poetry.

.. deprecated:: 0.8
   Use :func:`session` instead.

Import this module to monkey-patch Nox.
See :func:`nox_poetry.core.patch` for details.
"""
from nox_poetry.core import patch


patch()
