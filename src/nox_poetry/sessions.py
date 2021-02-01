"""Replacements for the ``nox.session`` decorator and the ``nox.Session`` class."""
import functools
from pathlib import Path
from typing import Any
from typing import Iterable

import nox

from nox_poetry.core import build_package
from nox_poetry.core import export_requirements
from nox_poetry.core import install
from nox_poetry.core import installroot
from nox_poetry.poetry import DistributionFormat


def session(*args: Any, **kwargs: Any) -> Any:
    """Drop-in replacement for the nox.session_ decorator.

    Use this decorator instead of ``@nox.session``. Session functions are passed
    :class:`Session` instead of ``nox.Session``; otherwise, the decorators work
    exactly the same.

    .. _nox.session:
        https://nox.thea.codes/en/stable/config.html#nox.session

    Args:
        args: Positional arguments are forwarded to ``nox.session``.
        kwargs: Keyword arguments are forwarded to ``nox.session``.

    Returns:
        The decorated session function.
    """
    if not args:
        return functools.partial(session, **kwargs)

    [function] = args

    @functools.wraps(function)
    def wrapper(session: nox.Session) -> None:
        proxy = Session(session)
        function(proxy)

    return nox.session(wrapper, **kwargs)  # type: ignore[call-overload]


class _PoetrySession:
    """Poetry-related utilities for session functions."""

    def __init__(self, session: nox.Session) -> None:
        """Initialize."""
        self.session = session

    def install(self, *args: str, **kwargs: Any) -> None:
        """Install packages into a Nox session using Poetry.

        This function installs packages into the session's virtual environment. It
        is a wrapper for `nox.sessions.Session.install`_, whose positional
        arguments are command-line arguments for `pip install`_, and whose keyword
        arguments are the same as those for `nox.sessions.Session.run`_.

        If a positional argument is ".", a wheel is built using
        :meth:`build_package`, and the argument is replaced with the file URL
        returned by that function. Otherwise, the argument is forwarded unchanged.

        In addition, a `constraints file`_ is generated for the package
        dependencies using :meth:`export_requirements`, and passed to ``pip
        install`` via its ``--constraint`` option. This ensures that any package
        installed will be at the version specified in Poetry's lock file.

        Every package passed to this function must be managed as a dependency in
        Poetry, to avoid an error due to missing archive hashes.

        .. _pip install: https://pip.pypa.io/en/stable/reference/pip_install/
        .. _nox.sessions.Session.install:
            https://nox.thea.codes/en/stable/config.html#nox.sessions.Session.install
        .. _nox.sessions.Session.run:
            https://nox.thea.codes/en/stable/config.html#nox.sessions.Session.run
        .. _constraints file:
            https://pip.pypa.io/en/stable/user_guide/#constraints-files

        Args:
            args: Command-line arguments for ``pip install``.
            kwargs: Keyword-arguments for ``session.install``. These are the same
                as those for `nox.sessions.Session.run`_.
        """
        install(self.session, *args, **kwargs)

    def installroot(
        self,
        *,
        distribution_format: DistributionFormat,
        extras: Iterable[str] = (),
    ) -> None:
        """Install the root package into a Nox session using Poetry.

        This function installs the package located in the current directory into the
        session's virtual environment.

        A constraints file is generated for the package dependencies using
        :meth:`export_requirements`, and passed to ``pip install`` via its
        ``--constraint`` option. This ensures that core dependencies are installed
        using the versions specified in Poetry's lock file.

        Args:
            distribution_format: The distribution format, either wheel or sdist.
            extras: Extras to install for the package.
        """
        installroot(
            self.session, distribution_format=distribution_format, extras=extras
        )

    def export_requirements(self) -> Path:
        """Export a requirements file from Poetry.

        This function uses `poetry export`_ to generate a `requirements file`_
        containing the project dependencies at the versions specified in
        ``poetry.lock``. The requirements file includes both core and development
        dependencies.

        The requirements file is stored in a per-session temporary directory,
        together with a hash digest over ``poetry.lock`` to avoid generating the
        file when the dependencies have not changed since the last run.

        .. _poetry export: https://python-poetry.org/docs/cli/#export
        .. _requirements file:
            https://pip.pypa.io/en/stable/user_guide/#requirements-files

        Returns:
            The path to the requirements file.
        """
        return export_requirements(self.session)

    def build_package(self, *, distribution_format: DistributionFormat) -> str:
        """Build a distribution archive for the package.

        This function uses `poetry build`_ to build a wheel or sdist archive for
        the local package, as specified via the ``distribution_format`` parameter.
        It returns a file URL with the absolute path to the built archive, and an
        embedded `SHA-256 hash`_ computed for the archive. This makes it suitable
        as an argument to `pip install`_ when a constraints file is also being
        passed, as in :meth:`install`.

        .. _poetry build: https://python-poetry.org/docs/cli/#export
        .. _pip install: https://pip.pypa.io/en/stable/reference/pip_install/
        .. _SHA-256 hash:
            https://pip.pypa.io/en/stable/reference/pip_install/#hash-checking-mode

        Args:
            distribution_format: The distribution format, either wheel or sdist.

        Returns:
            The file URL for the distribution package.
        """
        return build_package(self.session, distribution_format=distribution_format)


class _SessionProxy:
    """Proxy for nox.Session."""

    def __init__(self, session: nox.Session) -> None:
        """Initialize."""
        self._session = session

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to nox.Session."""
        return getattr(self._session, name)


class Session(_SessionProxy):
    """Proxy for nox.sessions.Session_, passed to user-defined session functions.

    .. _nox.sessions.Session:
        https://nox.thea.codes/en/stable/config.html#nox.sessions.Session

    This class overrides :meth:`session.install
    <nox_poetry.sessions._PoetrySession.install>`, and provides Poetry-related
    utilities:

    - :meth:`Session.poetry.installroot
      <nox_poetry.sessions._PoetrySession.installroot>`
    - :meth:`Session.poetry.build_package
      <nox_poetry.sessions._PoetrySession.build_package>`
    - :meth:`Session.poetry.export_requirements
      <nox_poetry.sessions._PoetrySession.export_requirements>`
    """

    def __init__(self, session: nox.Session) -> None:
        """Initialize."""
        super().__init__(session)
        self.poetry = _PoetrySession(session)

    def install(self, *args: str, **kwargs: Any) -> None:
        """Install packages into a Nox session using Poetry."""
        return self.poetry.install(*args, **kwargs)
