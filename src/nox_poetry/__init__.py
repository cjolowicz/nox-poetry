"""Using Poetry in Nox sessions.

This package provides a drop-in replacement for the :func:`session` decorator,
and for the :class:`Session` object passed to user-defined session functions.
This enables :meth:`session.install
<nox_poetry.sessions._PoetrySession.install>` to install packages at the
versions specified in the Poetry lock file.

Example:
    >>> @session(python=["3.8", "3.9"])
    ... def tests(session: Session) -> None:
    ...     session.install("pytest", ".")
    ...     session.run("pytest")

It also provides helper functions that allow more fine-grained control:

- :meth:`session.poetry.installroot
  <nox_poetry.sessions._PoetrySession.installroot>`
- :meth:`session.poetry.build_package
  <nox_poetry.sessions._PoetrySession.build_package>`
- :meth:`session.poetry.export_requirements
  <nox_poetry.sessions._PoetrySession.export_requirements>`

Two constants are defined to specify the format for distribution archives:

- :const:`WHEEL`
- :const:`SDIST`
"""
from nox_poetry.poetry import DistributionFormat
from nox_poetry.sessions import Session
from nox_poetry.sessions import session


#: A wheel archive.
WHEEL: str = DistributionFormat.WHEEL

#: A source archive.
SDIST: str = DistributionFormat.SDIST

__all__ = [
    "Session",
    "session",
    "SDIST",
    "WHEEL",
]
