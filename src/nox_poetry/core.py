"""Core functions.

.. deprecated:: 0.8
   Use :func:`session` instead.
"""
import warnings
from pathlib import Path
from typing import Any
from typing import Iterable
from typing import Optional

import nox.sessions

from nox_poetry.poetry import DistributionFormat
from nox_poetry.sessions import Session


Session_install = nox.sessions.Session.install


def _deprecate(name: str, replacement: Optional[str] = None) -> None:
    message = f"nox_poetry.{name} is deprecated, use @nox_poetry.session instead"
    if replacement is not None:
        message += f" and invoke {replacement}"
    warnings.warn(message, category=FutureWarning, stacklevel=2)


def export_requirements(session: nox.sessions.Session) -> Path:
    """Export a requirements file from Poetry.

    .. deprecated:: 0.8
       Use :func:`session` instead.
    """  # noqa: D
    _deprecate("export_requirements", "session.poetry.export_requirements")
    return Session(session).poetry.export_requirements()


def build_package(session: nox.sessions.Session, *, distribution_format: str) -> str:
    """Build a distribution archive for the package.  # noqa: DAR

    .. deprecated:: 0.8
       Use :func:`session` instead.
    """
    _deprecate("build_package", "session.poetry.build_package")
    return Session(session).poetry.build_package(
        distribution_format=distribution_format
    )


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


def patch(*, distribution_format: str = DistributionFormat.WHEEL) -> None:
    """Monkey-patch Nox to intercept ``session.install``.

    .. deprecated:: 0.8
       Use :func:`session` instead.

    This function monkey-patches `nox.sessions.Session.install`_ to invoke
    :func:`nox_poetry.install` instead. In addition, the argument ``"."`` is
    replaced by the specified distribution format, or :const:`nox_poetry.WHEEL`
    if none is specified.

    Instead of invoking this function directly, you can simply import
    :mod:`nox_poetry.patch`.

    .. _nox.sessions.Session.install:
       https://nox.thea.codes/en/stable/config.html#nox.sessions.Session.install

    Args:
        distribution_format: The distribution format to use when the ``"."``
            argument is encountered in calls to ``session.install``.
    """
    _deprecate("patch")
    nox.sessions.Session.install = install  # type: ignore[assignment]
