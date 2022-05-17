"""Core functions.

.. deprecated:: 0.8
   Use :func:`session` instead.
"""
import warnings
from typing import Any
from typing import Iterable
from typing import Optional

import nox.sessions

from nox_poetry.sessions import Session


Session_install = nox.sessions.Session.install


def _deprecate(name: str, replacement: Optional[str] = None) -> None:
    message = f"nox_poetry.{name} is deprecated, use @nox_poetry.session instead"
    if replacement is not None:
        message += f" and invoke {replacement}"
    warnings.warn(message, category=FutureWarning, stacklevel=2)


def install(session: nox.sessions.Session, *args: str, **kwargs: Any) -> None:
    """Install packages into a Nox session using Poetry.

    .. deprecated:: 0.8
       Use :func:`session` instead.
    """  # noqa: D
    _deprecate("install", "session.install")
    Session(session).install(*args, **kwargs)


def installroot(
    session: nox.sessions.Session,
    *,  # noqa: DAR
    distribution_format: str,
    extras: Iterable[str] = (),
) -> None:
    """Install the root package into a Nox session using Poetry.

    .. deprecated:: 0.8
       Use :func:`session` instead.
    """
    _deprecate("installroot", "session.poetry.installroot")
    Session(session).poetry.installroot(
        distribution_format=distribution_format, extras=extras
    )
