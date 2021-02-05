"""Core functions."""
from pathlib import Path
from typing import Any
from typing import Iterable

import nox.sessions

from nox_poetry.poetry import DistributionFormat
from nox_poetry.sessions import Session


Session_install = nox.sessions.Session.install


def export_requirements(session: nox.sessions.Session) -> Path:
    """Export a requirements file from Poetry."""
    return Session(session).poetry.export_requirements()


def build_package(
    session: nox.sessions.Session, *, distribution_format: DistributionFormat
) -> str:
    """Build a distribution archive for the package."""
    return Session(session).poetry.build_package(
        distribution_format=distribution_format
    )


def install(session: nox.sessions.Session, *args: str, **kwargs: Any) -> None:
    """Install packages into a Nox session using Poetry."""
    Session(session).install(*args, **kwargs)


def installroot(
    session: nox.sessions.Session,
    *,
    distribution_format: DistributionFormat,
    extras: Iterable[str] = (),
) -> None:
    """Install the root package into a Nox session using Poetry."""
    Session(session).poetry.installroot(
        distribution_format=distribution_format, extras=extras
    )


def patch(
    *, distribution_format: DistributionFormat = DistributionFormat.WHEEL
) -> None:
    """Monkey-patch Nox to intercept ``session.install``.

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
    nox.sessions.Session.install = install  # type: ignore[assignment]
