"""Replacements for the ``nox.session`` decorator and the ``nox.Session`` class."""
import functools
import hashlib
import re
from pathlib import Path
from typing import Any
from typing import Iterable
from typing import Iterator
from typing import Optional
from typing import Tuple

import nox
from packaging.requirements import InvalidRequirement
from packaging.requirements import Requirement

from nox_poetry.poetry import CommandSkippedError
from nox_poetry.poetry import DistributionFormat
from nox_poetry.poetry import Poetry


def session(*args: Any, **kwargs: Any) -> Any:
    """Drop-in replacement for the :func:`nox.session` decorator.

    Use this decorator instead of ``@nox.session``. Session functions are passed
    :class:`Session` instead of :class:`nox.sessions.Session`; otherwise, the
    decorators work exactly the same.

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
    def wrapper(session: nox.Session, *_args, **_kwargs) -> None:
        proxy = Session(session)
        function(proxy, *_args, **_kwargs)

    return nox.session(wrapper, **kwargs)  # type: ignore[call-overload]


_EXTRAS_PATTERN = re.compile(r"^(.+)(\[[^\]]+\])$")


def _split_extras(arg: str) -> Tuple[str, Optional[str]]:
    # From ``pip._internal.req.constructors._strip_extras``
    match = _EXTRAS_PATTERN.match(arg)
    if match:
        return match.group(1), match.group(2)
    return arg, None


def to_constraint(requirement_string: str, line: int) -> Optional[str]:
    """Convert requirement to constraint."""
    if any(
        requirement_string.startswith(prefix)
        for prefix in ("-", "file://", "git+https://", "http://", "https://")
    ):
        return None

    try:
        requirement = Requirement(requirement_string)
    except InvalidRequirement as error:
        raise RuntimeError(f"line {line}: {requirement_string!r}: {error}") from error

    if not (requirement.name and requirement.specifier):
        return None

    constraint = f"{requirement.name}{requirement.specifier}"
    return f"{constraint}; {requirement.marker}" if requirement.marker else constraint


def to_constraints(requirements: str) -> str:
    """Convert requirements to constraints."""

    def _to_constraints() -> Iterator[str]:
        lines = requirements.splitlines()
        for line, requirement in enumerate(lines, start=1):
            if requirement.strip():
                constraint = to_constraint(requirement, line)
                if constraint is not None:
                    yield constraint

    return "\n".join(_to_constraints())


class _PoetrySession:
    """Poetry-related utilities for session functions."""

    def __init__(self, session: nox.Session) -> None:
        """Initialize."""
        self.session = session
        self.poetry = Poetry(session)

    def install(self, *args: str, **kwargs: Any) -> None:
        """Install packages into a Nox session using Poetry.

        This function installs packages into the session's virtual environment. It
        is a wrapper for :meth:`nox.sessions.Session.install`, whose positional
        arguments are command-line arguments for :ref:`pip install`, and whose keyword
        arguments are the same as those for :meth:`nox.sessions.Session.run`.

        If a positional argument is ".", a wheel is built using
        :meth:`build_package`, and the argument is replaced with the file URL
        returned by that function. Otherwise, the argument is forwarded unchanged.

        In addition, a :ref:`constraints file <Constraints Files>` is generated
        for the package dependencies using :meth:`export_requirements`, and
        passed to ``pip install`` via its ``--constraint`` option. This ensures
        that any package installed will be at the version specified in Poetry's
        lock file.

        Args:
            args: Command-line arguments for ``pip install``.
            kwargs: Keyword-arguments for ``session.install``. These are the same
                as those for :meth:`nox.sessions.Session.run`.
        """
        args_extras = [_split_extras(arg) for arg in args]

        if "." in [arg for arg, _ in args_extras]:
            try:
                package = self.build_package()
            except CommandSkippedError:
                return

            def rewrite(arg: str, extras: Optional[str]) -> str:
                if arg != ".":
                    return arg if extras is None else arg + extras

                if extras is None:
                    return package

                name = self.poetry.config.name
                return f"{name}{extras} @ {package}"

            args = tuple(rewrite(arg, extras) for arg, extras in args_extras)

            self.session.run_always("pip", "uninstall", "--yes", package, silent=True)

        try:
            requirements = self.export_requirements()
        except CommandSkippedError:
            return

        self.session.install(f"--constraint={requirements}", *args, **kwargs)

    def installroot(
        self,
        *,
        distribution_format: str = DistributionFormat.WHEEL,
        extras: Iterable[str] = (),
    ) -> None:
        """Install the root package into a Nox session using Poetry.

        This function installs the package located in the current directory into the
        session's virtual environment.

        A :ref:`constraints file <Constraints Files>` is generated for the
        package dependencies using :meth:`export_requirements`, and passed to
        :ref:`pip install` via its ``--constraint`` option. This ensures that
        core dependencies are installed using the versions specified in Poetry's
        lock file.

        Args:
            distribution_format: The distribution format, either wheel or sdist.
            extras: Extras to install for the package.
        """
        try:
            package = self.build_package(distribution_format=distribution_format)
            requirements = self.export_requirements()
        except CommandSkippedError:
            return

        self.session.run_always("pip", "uninstall", "--yes", package, silent=True)

        suffix = ",".join(extras)
        if suffix.strip():
            suffix = suffix.join("[]")
            name = self.poetry.config.name
            package = f"{name}{suffix} @ {package}"

        if distribution_format == DistributionFormat.SDIST:
            # Remove the package from pip's wheel cache to prevent it from being
            # installed instead of a wheel built from our sdist. Treat an exit code of 1
            # as success; this means that the package was not in the wheel cache.
            name = self.poetry.config.name
            self.session.run_always(
                "pip", "cache", "remove", name, success_codes=[0, 1], silent=True
            )

        self.session.install(f"--constraint={requirements}", package)

    def export_requirements(self) -> Path:
        """Export a requirements file from Poetry.

        This function uses `poetry export <https://python-poetry.org/docs/cli/#export>`_
        to generate a :ref:`requirements file <Requirements Files>` containing the
        project dependencies at the versions specified in ``poetry.lock``. The
        requirements file includes both core and development dependencies.

        The requirements file is stored in a per-session temporary directory,
        together with a hash digest over ``poetry.lock`` to avoid generating the
        file when the dependencies have not changed since the last run.

        Returns:
            The path to the requirements file.
        """
        # Avoid ``session.virtualenv.location`` because PassthroughEnv does not
        # have it. We'll just create a fake virtualenv directory in this case.

        tmpdir = Path(self.session._runner.envdir) / "tmp"
        tmpdir.mkdir(exist_ok=True, parents=True)

        path = tmpdir / "requirements.txt"
        hashfile = tmpdir / f"{path.name}.hash"

        lockdata = Path("poetry.lock").read_bytes()
        digest = hashlib.blake2b(lockdata).hexdigest()

        if not hashfile.is_file() or hashfile.read_text() != digest:
            constraints = to_constraints(self.poetry.export())
            path.write_text(constraints)
            hashfile.write_text(digest)

        return path

    def build_package(
        self, *, distribution_format: str = DistributionFormat.WHEEL
    ) -> str:
        """Build a distribution archive for the package.

        This function uses `poetry build <https://python-poetry.org/docs/cli/#build>`_
        to build a wheel or sdist archive for the local package, as specified via the
        ``distribution_format`` parameter. It returns a file URL with the absolute path
        to the built archive.

        Args:
            distribution_format: The distribution format, either wheel or sdist.

        Returns:
            The file URL for the distribution package.
        """
        wheel = Path("dist") / self.poetry.build(format=distribution_format)
        url = wheel.resolve().as_uri()

        if DistributionFormat(distribution_format) is DistributionFormat.SDIST:
            url += f"#egg={self.poetry.config.name}"

        return url


class _SessionProxy:
    """Proxy for :class:`nox.sessions.Session`."""

    def __init__(self, session: nox.Session) -> None:
        """Initialize."""
        self._session = session

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to nox.Session."""
        return getattr(self._session, name)


class Session(_SessionProxy):
    """Proxy for :class:`nox.sessions.Session`, passed to session functions.

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
