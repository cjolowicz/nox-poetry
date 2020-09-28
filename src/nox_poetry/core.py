"""Core functions."""
import hashlib
from pathlib import Path
from typing import Any
from typing import List
from typing import Union

from nox.sessions import Session

from nox_poetry.poetry import DistributionFormat
from nox_poetry.poetry import Poetry


Session_install = Session.install


def export_requirements(session: Session) -> Path:
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

    Args:
        session: The ``Session`` object.

    Returns:
        The path to the requirements file.
    """
    tmpdir = Path(session.create_tmp())
    path = tmpdir / "requirements.txt"
    hashfile = tmpdir / f"{path.name}.hash"

    lockdata = Path("poetry.lock").read_bytes()
    digest = hashlib.blake2b(lockdata).hexdigest()

    if not hashfile.is_file() or hashfile.read_text() != digest:
        Poetry(session).export(path)
        hashfile.write_text(digest)

    return path


def build_package(session: Session, *, distribution_format: DistributionFormat) -> str:
    """Build a distribution archive for the package.

    This function uses `poetry build`_ to build a wheel or sdist archive for
    the local package, as specified via the ``distribution_format`` parameter.
    It returns a file URL with the absolute path to the built archive, and an
    embedded `SHA-256 hash`_ computed for the archive. This makes it suitable
    as an argument to `pip install`_ when a constraints file is also being
    passed, as in :func:`install`.

    .. _poetry build: https://python-poetry.org/docs/cli/#export
    .. _pip install: https://pip.pypa.io/en/stable/reference/pip_install/
    .. _SHA-256 hash:
       https://pip.pypa.io/en/stable/reference/pip_install/#hash-checking-mode

    Args:
        session: The ``Session`` object.
        distribution_format: The distribution format, either wheel or sdist.

    Returns:
        The file URL for the distribution package.
    """
    poetry = Poetry(session)
    wheel = Path("dist") / poetry.build(format=distribution_format)
    digest = hashlib.sha256(wheel.read_bytes()).hexdigest()

    return f"file://{wheel.resolve().as_posix()}#sha256={digest}"


def install(
    session: Session, *args: Union[DistributionFormat, str], **kwargs: Any
) -> None:
    """Install packages into a Nox session using Poetry.

    This function installs packages into the session's virtual environment. It
    is a wrapper for `nox.sessions.Session.install`_, whose positional
    arguments are command-line arguments for `pip install`_, and whose keyword
    arguments are the same as those for `nox.sessions.Session.run`_.

    If a positional argument is :const:`WHEEL` or :const:`SDIST`, a
    distribution archive is built using :func:`build_package`, and the argument
    is replaced with the file URL returned by that function. Otherwise, the
    argument is forwarded unchanged.

    In addition, a `constraints file`_ is generated for the package
    dependencies using :func:`export_requirements`, and passed to ``pip
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
        session: The Session object.
        args: Command-line arguments for ``pip install``. The constants
            :const:`WHEEL` and :const:`SDIST` are replaced by a distribution
            archive built for the local package.
        kwargs: Keyword-arguments for ``session.install``. These are the same
            as those for `nox.sessions.Session.run`_.
    """
    resolved = {
        arg: (
            build_package(session, distribution_format=arg)
            if isinstance(arg, DistributionFormat)
            else arg
        )
        for arg in args
    }

    for distribution_format in DistributionFormat:
        package = resolved.get(distribution_format)
        if package is not None:
            session.run("pip", "uninstall", "--yes", package, silent=True)

    requirements = export_requirements(session)
    Session_install(
        session, f"--constraint={requirements}", *resolved.values(), **kwargs
    )


def patch(
    *, distribution_format: DistributionFormat = DistributionFormat.WHEEL
) -> None:
    """Monkey-patch Nox to intercept ``session.install``.

    This function monkey-patches `nox.sessions.Session.install`_ to invoke
    :func:`install` instead. In addition, the argument ``"."`` is replaced by
    the specified distribution format, or :const:`WHEEL` if none is specified.

    Instead of invoking this function directly, you can simply import
    :mod:`nox_poetry.patch`.

    .. _nox.sessions.Session.install:
       https://nox.thea.codes/en/stable/config.html#nox.sessions.Session.install

    Args:
        distribution_format: The distribution format to use when the ``"."``
            argument is encountered in calls to ``session.install``.
    """

    def patched_install(self: Session, *args: str, **kwargs: Any) -> None:
        newargs: List[Union[DistributionFormat, str]] = [
            distribution_format if arg == "." else arg for arg in args
        ]
        install(self, *newargs, **kwargs)

    Session.install = patched_install  # type: ignore[assignment]
