"""Core functions.

.. deprecated:: 0.8
   Use :func:`session` instead.
"""
import warnings
from typing import Optional


def _deprecate(name: str, replacement: Optional[str] = None) -> None:
    message = f"nox_poetry.{name} is deprecated, use @nox_poetry.session instead"
    if replacement is not None:
        message += f" and invoke {replacement}"
    warnings.warn(message, category=FutureWarning, stacklevel=2)
