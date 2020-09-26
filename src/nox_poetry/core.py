"""Core functions."""
import hashlib
from pathlib import Path
from typing import Union

from nox.sessions import Session

from nox_poetry.poetry import DistributionFormat
from nox_poetry.poetry import Poetry


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


def build_package(session: Session, *, format: DistributionFormat) -> str:
    """Build a distribution archive for the package.

    Args:
        session: The Session object.
        format: The distribution format, either wheel or sdist.

    Returns:
        The file URL for the distribution package.
    """
    # Provide a hash for the wheel since the constraints file uses hashes.
    # https://pip.pypa.io/en/stable/reference/pip_install/#hash-checking-mode
    poetry = Poetry(session)
    wheel = Path("dist") / poetry.build(format=format)
    digest = hashlib.sha256(wheel.read_bytes()).hexdigest()

    return f"file://{wheel.resolve().as_posix()}#sha256={digest}"


def install(session: Session, *args: Union[DistributionFormat, str]) -> None:
    """Install packages into the session's virtual environment.

    This function is a wrapper for nox.sessions.Session.install.

    The packages must be managed as dependencies in Poetry.

    Args:
        session: The Session object.
        args: Command-line arguments for ``pip install``. The ``WHEEL``
            and ``SDIST`` constants are replaced by a wheel or sdist
            archive built from the local package.
    """
    resolved = {
        arg: (
            build_package(session, format=arg)
            if isinstance(arg, DistributionFormat)
            else arg
        )
        for arg in args
    }

    for format in DistributionFormat:
        package = resolved.get(format)
        if package is not None:
            session.run("pip", "uninstall", "--yes", package, silent=True)

    requirements = export_requirements(session)
    session.install(f"--constraint={requirements}", *resolved.values())
