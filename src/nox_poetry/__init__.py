"""Using Poetry in Nox sessions."""
import hashlib
from pathlib import Path

from nox.sessions import Session


class _Poetry:
    """Helper class for invoking Poetry inside a Nox session.

    Attributes:
        session: The Session object.
    """

    def __init__(self, session: Session) -> None:
        """Initialize."""
        self.session = session

    def export(self, path: Path, *, dev: bool) -> None:
        """Export the lock file to requirements format.

        Args:
            path: The destination path.
            dev: If True, include development dependencies.
        """
        options = ["--dev"] if dev else []
        self.session.run(
            "poetry",
            "export",
            "--format=requirements.txt",
            f"--output={path}",
            *options,
            external=True,
        )

    def build(self, *args: str) -> str:
        """Build the package.

        Args:
            args: Command-line arguments for ``poetry build``.

        Returns:
            The basename of the wheel built by Poetry.
        """
        output = self.session.run(
            "poetry", "build", *args, external=True, silent=True, stderr=None
        )
        assert isinstance(output, str)  # noqa: S101
        return output.split()[-1]


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
        _Poetry(session).export(path, dev=dev)
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
    poetry = _Poetry(session)
    wheel = poetry.build("--format=wheel")
    requirements = export_requirements(session, dev=False)

    session.install(f"--requirement={requirements}")
    session.install("--no-deps", "--force-reinstall", f"dist/{wheel}")


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
