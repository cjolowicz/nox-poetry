"""Using Poetry in Nox sessions.

This package provides a drop-in replacement for the :func:`session` decorator,
and for the :class:`Session` object passed to user-defined session functions.
This enables :meth:`session.install <nox_poetry.PoetrySession.install>` to
install packages at the versions specified in the Poetry lock file.

Example:
    >>> @session(python=["3.8", "3.9"])
    ... def tests(session: Session) -> None:
    ...     session.install("pytest", ".")
    ...     session.run("pytest")

The :class:`PoetrySession` class provides utilities that allow more fine-grained
control:

- :meth:`PoetrySession.install`
- :meth:`PoetrySession.installroot`
- :meth:`PoetrySession.build_package`
- :meth:`PoetrySession.export_requirements`

Two constants are defined to specify the format for distribution archives:

- :const:`WHEEL`
- :const:`SDIST`
"""
from nox_poetry.core import build_package
from nox_poetry.core import export_requirements
from nox_poetry.core import install
from nox_poetry.core import installroot
from nox_poetry.poetry import DistributionFormat
from nox_poetry.sessions import PoetrySession
from nox_poetry.sessions import Session
from nox_poetry.sessions import session


#: A wheel archive.
WHEEL: str = DistributionFormat.WHEEL

#: A source archive.
SDIST: str = DistributionFormat.SDIST

__all__ = [
    "build_package",
    "export_requirements",
    "install",
    "installroot",
    "PoetrySession",
    "Session",
    "session",
    "SDIST",
    "WHEEL",
]
