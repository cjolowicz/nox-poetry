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
    """Export the lock file to requirements format.

    Args:
        session: The Session object.

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

    Args:
        session: The Session object.
        distribution_format: The distribution format, either wheel or sdist.

    Returns:
        The file URL for the distribution package.
    """
    # Provide a hash for the wheel since the constraints file uses hashes.
    # https://pip.pypa.io/en/stable/reference/pip_install/#hash-checking-mode
    poetry = Poetry(session)
    wheel = Path("dist") / poetry.build(format=distribution_format)
    digest = hashlib.sha256(wheel.read_bytes()).hexdigest()

    return f"file://{wheel.resolve().as_posix()}#sha256={digest}"


def install(
    session: Session, *args: Union[DistributionFormat, str], **kwargs: Any
) -> None:
    """Install packages into the session's virtual environment.

    This function is a wrapper for ``nox.sessions.Session.install``.

    The packages must be managed as dependencies in Poetry.

    Args:
        session: The Session object.
        args: Command-line arguments for ``pip install``. The ``WHEEL``
            and ``SDIST`` constants are replaced by a wheel or sdist
            archive built from the local package.
        kwargs: Keyword-arguments for ``session.install``.
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
    """Monkey-patch nox.sessions.Session.install with nox_poetry.install."""

    def patched_install(self: Session, *args: str, **kwargs: Any) -> None:
        newargs: List[Union[DistributionFormat, str]] = [
            distribution_format if arg == "." else arg for arg in args
        ]
        install(self, *newargs, **kwargs)

    Session.install = patched_install  # type: ignore[assignment]
