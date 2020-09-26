"""Core functions."""
import hashlib
from pathlib import Path

from nox.sessions import Session

from nox_poetry.poetry import Poetry


def export_requirements(session: Session, *, dev: bool) -> Path:
    """Export the lock file to requirements format.

    Args:
        session: The Session object.
        dev: If True, include development dependencies.

    Returns:
        The path to the requirements file.
    """
    tmpdir = Path(session.create_tmp())
    name = "dev-requirements.txt" if dev else "requirements.txt"
    path = tmpdir / name
    hashfile = tmpdir / f"{name}.hash"

    lockdata = Path("poetry.lock").read_bytes()
    digest = hashlib.blake2b(lockdata).hexdigest()

    if not hashfile.is_file() or hashfile.read_text() != digest:
        Poetry(session).export(path, dev=dev)
        hashfile.write_text(digest)

    return path


def install_package(session: Session) -> None:
    """Build and install the package.

    Build a wheel from the package, and install it into the virtual environment
    of the specified Nox session.

    The package requirements are installed using the versions specified in
    Poetry's lock file.

    Args:
        session: The Session object.
    """
    requirements = export_requirements(session, dev=False)

    # Provide a hash for the wheel since its requirements have hashes.
    # https://pip.pypa.io/en/stable/reference/pip_install/#hash-checking-mode
    poetry = Poetry(session)
    wheel = Path("dist") / poetry.build("--format=wheel")
    digest = hashlib.sha256(wheel.read_bytes()).hexdigest()

    session.run("pip", "uninstall", "--yes", str(wheel))
    session.install(
        f"--constraint={requirements}",
        f"file://{wheel.resolve()}#sha256={digest}",
    )


def install(session: Session, *args: str) -> None:
    """Install development dependencies into the session's virtual environment.

    This function is a wrapper for nox.sessions.Session.install.

    The packages must be managed as development dependencies in Poetry.

    Args:
        session: The Session object.
        args: Command-line arguments for ``pip install``.
    """
    requirements = export_requirements(session, dev=True)
    session.install(f"--constraint={requirements}", *args)
